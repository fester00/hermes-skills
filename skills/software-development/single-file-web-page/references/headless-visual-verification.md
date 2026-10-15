# Headless visual verification

Verify a rendered page's real behaviour with one-shot `google-chrome --headless=new` runs — no browser
daemon, no automation harness, no extra Python packages.

## 0. Base commands

```bash
CH="/usr/bin/google-chrome --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
--no-first-run --hide-scrollbars --user-data-dir=$SCRATCH/chrome-verify"

$CH --virtual-time-budget=8000 --window-size=1280,900 --screenshot=out.png file:///abs/page.html
$CH --virtual-time-budget=9000 --dump-dom file:///abs/page.html | grep -o 'SELFTEST=.*</pre>'
```

`--virtual-time-budget` advances timers, so page `setTimeout` callbacks run; `--dump-dom` prints the DOM
after that budget and exits. Use a dedicated `--user-data-dir` under the scratch dir, and prefer several
short foreground runs over one long-lived debug browser.

## 1. Self-test: let the page report its own state

Copy the page, append a script before `</body>` that measures and writes its result into the document:

```html
<script>
setTimeout(function(){
  var out = {};
  out.errors = window.__err || [];
  out.counts = document.querySelectorAll('.layer').length;
  out.particles = document.querySelectorAll('.firefly').length;   // JS-created nodes prove the script ran
  out.transforms = [].map.call(document.querySelectorAll('.layer'),
    function(l){ return getComputedStyle(l).transform; });
  var pre = document.createElement('pre'); pre.id = 'selftest';
  pre.textContent = 'SELFTEST=' + JSON.stringify(out);
  document.body.appendChild(pre);
}, 800);
</script>
```

Register `window.addEventListener('error', ...)` that pushes into `window.__err` so a throwing script is
visible in the same report instead of silently producing zero nodes.

## 2. `requestAnimationFrame` does not run in dump-dom mode

Headless dump runs no compositor frames, so rAF callbacks are starved and any state written from a rAF loop
stays at its initial value. Inject a stub in `<head>` **before** the page's own script:

```html
<script>window.requestAnimationFrame=function(cb){return setTimeout(function(){cb(performance.now());},0);};</script>
```

The self-test then sees the real wiring: scroll → listener → rAF → CSS variable → computed transform.

## 3. Prove the animation moves

1. Set the driver variable directly (`document.documentElement.style.setProperty('--sy', 1600)`) and read
   `getComputedStyle(layer).transform` for every layer.
2. Check the planes differ in the designed ratio (e.g. −160 / −416 / −832 px for 0.10 / 0.26 / 0.52).
3. Then scroll for real (`window.scrollTo(0, 1600)` + `dispatchEvent(new Event('scroll'))`) and confirm the
   page itself wrote the variable.

`matrix(a, b, c, d, tx, ty)` — index 5 is `translateY` for the common 2-D case.

## 4. Screenshot content checks with the standard library only

```python
import zlib, struct
data = png.read_bytes(); w, h = struct.unpack(">II", data[16:24])
idat, pos = b"", 8
while pos < len(data):
    ln, typ = struct.unpack(">I4s", data[pos:pos+8])
    if typ == b"IDAT": idat += data[pos+8:pos+8+ln]
    pos += 12 + ln
img = zlib.decompress(idat); stride = w*3 + 1
vals = [img[y*stride+1+x*3] for y in range(0, h, 30) for x in range(0, w, 30)]
```

- Uniform brightness ⇒ the page rendered nothing. Non-trivial spread ⇒ real content.
- "Bright" pixels (channel value > ~110 on dark surfaces) approximate text coverage; compare two variants
  (real page vs a copy with the hidden state forced to `opacity:0 !important`) to prove a reveal really
  changed what is on screen.
- Measure per horizontal band to see *where* content landed (hero vs story section).

## 5. Look at the frame

Statistics cannot tell body text from a decorative blob. Load the screenshot with `vision_analyze` and ask
specifically: is the expected heading and body copy visible, does anything overlap, are edges cut. This is how
content that exists in the DOM but is invisible on screen gets caught.

## 6. Simulating a script-less browser

`--blink-settings=scriptEnabled=false` is not honoured by every build. Exact and simpler: copy the page and
delete the inline `js`-class line — that is precisely the state a browser without scripts has. Screenshot both
variants and compare the bright-pixel share; they must match.

## 7. Hygiene

Delete the temporary copies and test HTML after each run, keep only the screenshots you quote, and never
mutate the deliverable in order to test it.

## 8. Phone-width and end-of-page checks

Headless Chrome clamps `--window-size` to a **500×701 minimum**: ask for 390 px and you silently get 500, so
`max-width:640px` rules never fire and the “mobile” screenshot proves nothing. Put the page in a 390 px iframe
inside the 500 px window — the inner document resolves media queries and `vh`/`dvh` against the iframe:

```html
<div style="width:390px;height:844px;overflow:hidden">
  <iframe src="page.html" style="width:390px;height:844px;border:0"></iframe>
</div>
```

`file://` iframes are cross-origin to the parent, so you cannot drive them from outside: make a copy that
scrolls itself on `load` (`window.scrollTo(0, document.documentElement.scrollHeight)`), plus one with the hero
hidden when a mid-page section must be in frame.

For the end of the page report, per layer: `top`/`bottom`, which layers still cover `innerHeight - 8`, and
whether the panels are revealed. Two artefacts to expect and not misread:

- **Transitions never advance.** `getComputedStyle(node).opacity` keeps reporting the pre-transition value
  (`0`) even after the reveal class is applied, because dump mode produces no compositor frames. Assert the
  *class* (`.panel.in`) and confirm the pixels in a screenshot; never conclude from the computed number alone
  that the text is invisible.
- **Screenshot mode captures early.** A copy that scrolls on a timer can be captured before the scroll runs;
  for screenshots drive the scroll immediately at parse time, and keep the timer variant for dump assertions.
