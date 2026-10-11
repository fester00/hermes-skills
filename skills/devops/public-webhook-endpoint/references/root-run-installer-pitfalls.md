# Pitfalls of Setup Scripts That Run as Root

Each of these produced a failure that looked like something else entirely.

## Never put `*` inside a variable holding a command
```bash
CURL="curl -fsSL --noproxy *"      # WRONG
$CURL https://host/file            # * expands to the directory listing
```
The shell expands the glob before the variable is used, so curl receives every filename in the
current directory as a URL: a wall of `Could not resolve host: config.yaml`. Write the flag inline
and quoted — `curl -fsSL --noproxy '*' ...`. If this slipped through, the destination file ends up
holding whatever page the local catch-all web server returned for those names.

## Temporary files: `mktemp -d`, never a fixed `/tmp` filename
With `fs.protected_regular=2` (Ubuntu default) plus the sticky bit on `/tmp`, **root cannot open an
existing `/tmp` file owned by another user for writing.** A script run once as the normal user
leaves `/tmp/<fixed-name>` behind; the sudo run then dies with
`curl: (23) Failure writing output to destination`, which reads like a disk or network fault.
```bash
WORK=$(mktemp -d "${TMPDIR:-/tmp}/<app>.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
```

## Retry downloads, validate them, and only then touch /etc
Flaky TLS to package hosts is intermittent — three attempts with a short pause turn a hard failure
into a success on attempt 2 or 3. Validate the artifact before installing it:
```bash
file -b "$WORK/key.gpg" | grep -qi OpenPGP || { head -c 160 "$WORK/key.gpg"; exit 1; }
grep -q '^deb' "$WORK/list"              || { head -c 160 "$WORK/list"; exit 1; }
```
A failed download piped straight into `install`/`tee` writes an HTML error page into
`/etc/apt/sources.list.d/`, and afterwards every `apt-get update` fails with
`Неизвестный тип «<!DOCTYPE»`. That is a package manager broken by a script, not by apt.

## Make the script repair what a previous bad run left behind
Put detection/cleanup at the top so the user can simply re-run it:
```bash
if [ -e "$LIST" ] && { grep -qi '<!DOCTYPE' "$LIST" || grep -qi '<html' "$LIST" \
   || ! grep -q '^deb' "$LIST"; }; then sudo rm -f "$LIST"; fi
if [ -e "$KEYRING" ] && ! file -b "$KEYRING" | grep -qi OpenPGP; then sudo rm -f "$KEYRING"; fi
```
The explicit HTML test is required: the corrupted sources file contained an `<html>` page *and* a
line beginning with `deb`, so a `^deb` check alone judged it valid.

## Kill by port, not by `pgrep -f <pattern>`
`pgrep -f` / `pkill -f` match the invoking shell's own command line, so a script that kills by
pattern can SIGTERM itself mid-run (the session dies with exit code -15 and no further output):
```bash
PID=$(ss -tlnp 2>/dev/null | grep ':8788' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)
[ -n "$PID" ] && kill "$PID"
```
In loops over `pgrep -f`, guard each hit with `[ "$p" != "$$" ]`.

## Before handing a script to the user
- `bash -n script.sh` passes; keep `set -euo pipefail` so a failed download stops the run instead of
  silently continuing.
- Dry-run every stage that needs no privileges yourself (download, validation, port checks) and
  report the real output. The user should only be supplying the password.
- Print step markers (`== 3/5. ... ==`) and keep failure messages actionable.
- Prefer a script that reports what it would do over one that guesses; a half-applied privileged
  change is much worse than a stop with a clear message.
