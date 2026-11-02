#!/usr/bin/env python3
"""Художественная ретушь портрета: ББ, плёночная кривая, маска кожи,
глаза/губы по долям кадра, успокоение фона, split-tone, винъетка, зерно.

Портретная часть (сглаживание кожи с текстуру, гашение блика) — в retouch_portrait.py;
этот скрипт — про авторский лук и про то, чтобы фон не спорил с лицом.

usage:
  portrait_art.py in.jpg out.jpg [crop=x1,y1,x2,y2] [key=value ...]
  portrait_art.py noise a.jpg b.jpg ...        # замер шума, без обработки

Параметры (по умолчанию):
  skin=0.50       доля подмешивания сглаженной кожи (0.4–0.6; больше — пластик)
  bg_sat=0.80     насыщенность фона (0.7–0.85; ниже 0.65 комната становится серой)
  bg_val=0.96     яркость фона
  bg_blur=0.0022  радиус размытия фона как доля ширины
  bg_mix=0.5      сколько оставить резкого фона
  warm=0.022      тёплые света (split-tone)
  cool=0.015      холодные тени
  vig=0.16        винъетка
  grain=2.4       зерно В ЕДИНИЦАХ КАДРА 1280 px — масштабируется по размеру картинки
  bw=1            ч/б
"""
import cv2, numpy as np, sys, json

REF_SIDE = 1280.0          # опорная короткая сторона для зерна


def measure_noise(paths):
    """Высокочастотный шум по плоским участкам теней: моё это зерно или камеры."""
    for p in paths:
        a = cv2.imread(p)
        if a is None:
            print(f'  {p}: не открылся')
            continue
        g = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY).astype(np.float32)
        hp = g - cv2.GaussianBlur(g, (0, 0), 1.2)
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        m = ((np.abs(gx) + np.abs(gy)) < 12) & (g < np.percentile(g, 35))
        print(f'  {p:38} шум в плоских тенях={hp[m].std():5.2f}  по кадру={hp.std():5.2f}')


def run(SRC, DST, argv):
    P = dict(skin=0.50, bg_sat=0.80, bg_val=0.96, bg_blur=0.0022, bg_mix=0.5,
             warm=0.022, cool=0.015, grain=2.4, vig=0.16, bw=False)
    CROP = None
    for a in argv:
        if a.startswith('crop='):
            CROP = [int(v) for v in a.split('=')[1].split(',')]
        elif '=' in a:
            k, v = a.split('=', 1)
            P[k] = (v == '1') if k == 'bw' else float(v)

    img = cv2.imread(SRC, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f'не открылся: {SRC}')
    if CROP:
        img = img[CROP[1]:CROP[3], CROP[0]:CROP[2]].copy()
    H, W = img.shape[:2]
    f = img.astype(np.float32) / 255.0

    # 1. баланс белого по нейтральным пикселям (чёрное/белое в кадре)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    neut = (hsv[..., 1] < 48) & (hsv[..., 2] > 45) & (hsv[..., 2] < 235)
    if neut.sum() > 500:
        m = [float(f[..., i][neut].mean()) for i in range(3)]
        ref = sum(m) / 3
        for i in range(3):
            f[..., i] *= ref / max(m[i], 1e-3)

    # 2. тональная кривая: тени поднять, света скатить
    f = np.clip((f * 2 ** 0.10), 0, 1)
    x = np.power(f, 0.97)
    x = x * 0.945 + 0.055 * np.power(x, 0.55)
    f = np.clip(x - 0.12 * np.power(np.clip(x, 0, 1), 4), 0, 1)

    # 3. маски: эллипс субъекта + кожа по YCbCr
    sub = np.zeros((H, W), np.float32)
    cv2.ellipse(sub, (int(W * .53), int(H * .60)), (int(W * .40), int(H * .52)), 0, 0, 360, 1.0, -1)
    sub = cv2.GaussianBlur(sub, (0, 0), min(W, H) * 0.06)
    ycc = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = ycc[..., 0], ycc[..., 1], ycc[..., 2]
    skin = ((Y > 45) & (Cr > 132) & (Cr < 178) & (Cb > 74) & (Cb < 130)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    skin = cv2.GaussianBlur(skin.astype(np.float32) * np.clip(sub, 0, 1), (0, 0), 3.0)[..., None]

    # 4. кожа: билитерал, затем выравнивание красноты по a-каналу
    smooth = cv2.bilateralFilter(img, 9, 42, 42).astype(np.float32) / 255.0
    k = P['skin']
    f = f * (1 - k * skin) + smooth * (k * skin)
    lab = cv2.cvtColor((np.clip(f, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    a_soft = cv2.bilateralFilter(lab[..., 1].astype(np.uint8), 15, 60, 25).astype(np.float32)
    lab[..., 1] = lab[..., 1] * (1 - .40 * skin[..., 0]) + a_soft * (.40 * skin[..., 0])
    f = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32) / 255.0

    # 5. глаза и губы — координаты в долях кадра, при кропе их надо пересчитать
    def boost(imgf, box, amount=1.0, bright=0.0, sat=1.0):
        x1, y1, x2, y2 = [max(0, min(int(v), s)) for v, s in zip(box, (W, H, W, H))]
        if x2 <= x1 or y2 <= y1:
            return imgf
        roi = imgf[y1:y2, x1:x2]
        roi = np.clip(roi + amount * (roi - cv2.GaussianBlur(roi, (0, 0), 1.1)) + bright, 0, 1)
        if sat != 1.0:
            hh = cv2.cvtColor((roi * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
            hh[..., 1] = np.clip(hh[..., 1] * sat, 0, 255)
            roi = cv2.cvtColor(hh.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0
        out = imgf.copy(); out[y1:y2, x1:x2] = roi
        return out

    for box in ((W * .395, H * .415, W * .500, H * .462), (W * .590, H * .408, W * .700, H * .455)):
        f = boost(f, box, amount=1.25, bright=0.025)
    f = boost(f, (W * .450, H * .478, W * .630, H * .545), amount=0.55, bright=0.010, sat=1.10)

    # 6. split-tone
    lum = f.mean(axis=2, keepdims=True)
    f[..., 2] = np.clip(f[..., 2] + P['warm'] * lum[..., 0] ** 2, 0, 1)
    f[..., 0] = np.clip(f[..., 0] + P['cool'] * (1 - lum[..., 0]) ** 2, 0, 1)

    img8 = (np.clip(f, 0, 1) * 255).astype(np.uint8)
    hh = cv2.cvtColor(img8, cv2.COLOR_BGR2HSV).astype(np.float32)
    hh[..., 1] = np.clip(hh[..., 1] * 1.05, 0, 255)
    img8 = cv2.cvtColor(hh.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 7. фон тише: цвет, яркость, мягкость — по маске субъекта
    if P['bg_sat'] != 1.0 or P['bg_val'] != 1.0 or P['bg_blur'] > 0:
        bh = cv2.cvtColor(img8, cv2.COLOR_BGR2HSV).astype(np.float32)
        bh[..., 1] *= P['bg_sat']
        bh[..., 2] *= P['bg_val']
        quiet = cv2.cvtColor(np.clip(bh, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        soft = cv2.GaussianBlur(quiet, (0, 0), max(1.0, W * P['bg_blur']))
        bg = quiet * P['bg_mix'] + soft * (1 - P['bg_mix'])
        subm = np.clip(sub, 0, 1)[..., None]
        img8 = (img8.astype(np.float32) * (1 - subm) + bg * subm).astype(np.uint8)

    # 8. ч/б
    if P['bw']:
        lm = cv2.cvtColor(img8, cv2.COLOR_BGR2LAB).astype(np.float32)
        L = np.clip((lm[..., 0] - 128) * 1.06 + 130, 0, 255)
        img8 = cv2.cvtColor(np.dstack([L, np.full_like(L, 128), np.full_like(L, 128)]).astype(np.uint8),
                            cv2.COLOR_LAB2BGR)

    # 9. винъетка
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = 1 - P['vig'] * np.clip((rr - .55) / .85, 0, 1) ** 1.4
    img8 = np.clip(img8.astype(np.float32) * vig[..., None], 0, 255).astype(np.uint8)

    # 10. зерно, ОТМАСШТАБИРОВАННОЕ по размеру кадра
    grain_eff = P['grain'] * (min(W, H) / REF_SIDE)
    if min(W, H) < 800:
        grain_eff = 0.0
    if grain_eff > 0:
        rng = np.random.default_rng(11)
        n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
        n /= (np.abs(n).max() + 1e-6)
        shw = 1.0 - np.clip(img8.mean(axis=2) / 255.0, 0, 1) ** 0.8
        img8 = np.clip(img8.astype(np.float32) + grain_eff * 255 * 0.05 * n[..., None] * shw[..., None],
                       0, 255).astype(np.uint8)

    cv2.imwrite(DST, img8, [int(cv2.IMWRITE_JPEG_QUALITY), 96])
    print(json.dumps({'out': DST, 'size': [W, H], 'grain_used': round(grain_eff, 2)}))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'noise':
        measure_noise(sys.argv[2:])
    elif len(sys.argv) > 2:
        run(sys.argv[1], sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
