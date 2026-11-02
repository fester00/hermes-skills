#!/usr/bin/env python3
"""Портретная ретушь: WB -> тон -> кожа -> блик -> глаза -> фон -> грейд.

Использование:
    python retouch_portrait.py in.jpg out.jpg '{"crop":[x0,y0,x1,y1], "smooth":0.4, ...}'

Все параметры необязательны; дефолты проверены на плоском комнатном свете.
Требуется opencv-python-headless.
"""
import cv2, numpy as np, sys, json

SRC = sys.argv[1] if len(sys.argv) > 1 else 'in.jpg'
DST = sys.argv[2] if len(sys.argv) > 2 else 'out.jpg'
P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

img = cv2.imread(SRC, cv2.IMREAD_COLOR)
if img is None:
    raise SystemExit('не читается ' + SRC)
crop = P.get('crop')                      # [x0, y0, x1, y1] — убрать потолок/углы
if crop:
    img = img[crop[1]:crop[3], crop[0]:crop[2]].copy()
h, w = img.shape[:2]

# ---------- 1. баланс белого по «серым» пикселям (стена/фон) ----------
hsv0 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lab0 = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
cand = (lab0[:, :, 0] > 95) & (lab0[:, :, 0] < 230) & (hsv0[:, :, 1] < 35)
if cand.sum() > 2000:
    b, g, r = [float(img[:, :, i][cand].mean()) for i in range(3)]
    m = (b + g + r) / 3.0
    gain = 1.0 + (np.array([m / b, m / g, m / r], np.float32) - 1.0) * P.get('wb', 0.7)
    img = np.clip(img.astype(np.float32) * gain, 0, 255).astype(np.uint8)

# ---------- 2. тональная кривая (LAB, только L) ----------
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0] / 255.0
L = L + P.get('shadow_lift', 0.04) * (1 - L) ** 2
L = L - P.get('hl_roll', 0.06) * np.clip(L - 0.78, 0, 1) ** 1.5
L = np.clip((L - 0.5) * (1 + P.get('contrast', 0.10)) + 0.5, 0, 1)
lab[:, :, 0] = L * 255
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- 3. маска кожи (лицо + шея) ----------
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
Y, Cr, Cb = ycrcb[:, :, 0], ycrcb[:, :, 1], ycrcb[:, :, 2]
m = ((Cr > 132) & (Cr < 180) & (Cb > 75) & (Cb < 132) & (Y > 45) & (Y < 252)).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
n, lbl, st, _ = cv2.connectedComponentsWithStats(m, 8)
if n > 1:
    m = (lbl == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
skin_soft = cv2.GaussianBlur((m * 255).astype(np.float32), (0, 0), 8) / 255.0
skin = np.clip(skin_soft * 1.1, 0, 1)[..., None]

# ---------- 4. кожа: билатеральное сглаживание + возврат текстуры ----------
amt = P.get('smooth', 0.40)
tex_amt = P.get('texture', 0.50)
bil = cv2.bilateralFilter(img, 13, 34, 13)
med = cv2.medianBlur(img, 5)
sm = cv2.addWeighted(bil, 0.6, med, 0.4, 0)
tex = cv2.addWeighted(img.astype(np.float32), 1.0, sm.astype(np.float32), -1.0, 128.0)
tex = cv2.addWeighted(tex, tex_amt, 128 * np.ones_like(tex), 1 - tex_amt, 0)
base = np.clip(sm.astype(np.float32) + (tex - 128.0), 0, 255)
img = np.where(skin > 0, img.astype(np.float32) * (1 - amt) + base * amt, img.astype(np.float32))
img = np.clip(img, 0, 255).astype(np.uint8)

# ---------- 5. блик на коже: гасим по локальному превышению (без порога и кромок) ----------
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
loc = cv2.GaussianBlur(L, (0, 0), 38)
spec = np.maximum(L - loc, 0.0)
L = L - P.get('shine', 0.25) * spec * skin[..., 0]
shp = L - cv2.GaussianBlur(L, (0, 0), 26)
L = L + P.get('shaping', 0.0) * shp * skin[..., 0]   # 0 на коже: иначе пятна и «электрические» блики
lab[:, :, 0] = np.clip(L, 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- 6. глаза: два тёмных клякса в средней трети -> белки, микроконтраст, искра ----------
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
band = np.zeros_like(gray, np.uint8)
band[int(h * 0.25):int(h * 0.55), int(w * 0.2):int(w * 0.8)] = 1
dark = ((gray < 90) & (band > 0)).astype(np.uint8) * 255
dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
n, lbl, st, cen = cv2.connectedComponentsWithStats(dark, 8)
eyes = []
if n > 1:
    for i in sorted(range(1, n), key=lambda i: -st[i, cv2.CC_STAT_AREA])[:2]:
        if st[i, cv2.CC_STAT_AREA] > 120:
            cx, cy = int(cen[i][0]), int(cen[i][1])
            rw = int(st[i, cv2.CC_STAT_WIDTH] * 0.62) + 8
            rh = int(st[i, cv2.CC_STAT_HEIGHT] * 0.85) + 8
            eyes.append((cx, cy, max(rw, 14), max(rh, 10)))
if eyes:
    emask = np.zeros((h, w), np.float32)
    for cx, cy, rw, rh in eyes:
        cv2.ellipse(emask, (cx, cy), (rw, rh), 0, 0, 360, 1.0, -1)
    emask = cv2.GaussianBlur(emask, (0, 0), 6)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[:, :, 0]
    light = np.clip((L - 110) / 145, 0, 1) * emask
    L = L + P.get('eye_light', 10.0) * light
    det = L - cv2.GaussianBlur(L, (0, 0), 1.8)
    L = L + P.get('eye_clarity', 0.45) * det * emask
    for cx, cy, rw, rh in eyes:                     # искра в зрачке — синтетика, назвать в ответе
        roi = L[max(cy - rh, 0):cy + rh, max(cx - rw, 0):cx + rw]
        if roi.size:
            spark = (roi >= np.percentile(roi, 92)).astype(np.float32)
            roi += P.get('catchlight', 18.0) * cv2.GaussianBlur(spark, (0, 0), 1.2)
    lab[:, :, 0] = np.clip(L, 0, 255)
    img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- 7. фон: блюр + затемнение + обесцвечивание ----------
bgw = cv2.GaussianBlur((1 - skin_soft).astype(np.float32), (0, 0), 22)[..., None]
blurred = cv2.GaussianBlur(img, (0, 0), P.get('bg_blur', 3.2))
img = np.clip(img.astype(np.float32) * (1 - bgw) + blurred.astype(np.float32) * bgw, 0, 255).astype(np.uint8)
img = np.clip(img.astype(np.float32) * (1 - P.get('bg_darken', 0.20) * bgw), 0, 255).astype(np.uint8)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
hsv[:, :, 1] *= (1 - P.get('bg_desat', 0.22) * bgw[..., 0])
img = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)

# ---------- 8. винъетка ----------
yy, xx = np.mgrid[0:h, 0:w]
d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
vig = 1 - P.get('vignette', 0.20) * np.clip(d - 0.6, 0, 1.4) ** 1.5
img = np.clip(img.astype(np.float32) * vig[..., None], 0, 255).astype(np.uint8)

# ---------- 9. резкость: только вне кожи ----------
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
hi = L - cv2.GaussianBlur(L, (0, 0), 1.3)
lab[:, :, 0] = np.clip(L + P.get('sharpen', 0.55) * (1 - 0.85 * skin[..., 0]) * hi, 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- 10. чёрная точка, грейд, насыщенность ----------
f = img.astype(np.float32)
blk = P.get('black', 3.0)
f = np.clip((f - blk) * (255.0 / (255.0 - blk)), 0, 255)
img = cv2.cvtColor(f.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
a, b = img[:, :, 1] - 128, img[:, :, 2] - 128
lum = img[:, :, 0] / 255.0
a += P.get('grade_a', 3.5) * (lum - 0.5)
b += P.get('grade_b', 6.5) * (lum - 0.45)
img[:, :, 1] = np.clip(a + 128, 0, 255)
img[:, :, 2] = np.clip(b + 128, 0, 255)
img = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
hsv[:, :, 1] = np.clip(hsv[:, :, 1] * P.get('sat', 1.05), 0, 255)
img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

# ---------- 11. тепло кожи (только маска) ----------
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
lab[:, :, 2] = np.clip(lab[:, :, 2] + P.get('skin_warm', 3.0) * skin[..., 0], 0, 255)
lab[:, :, 1] = np.clip(lab[:, :, 1] + P.get('skin_magenta', 1.2) * skin[..., 0], 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- 12. финальное сжатие светов (без него лоб/нос выжигаются) ----------
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0] / 255.0
L = L - P.get('hl_final', 0.5) * np.maximum(L - 0.82, 0.0)
lab[:, :, 0] = np.clip(L, 0, 1) * 255
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

cv2.imwrite(DST, img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
print(json.dumps({'out': DST, 'size': [int(w), int(h)], 'eyes_detected': bool(eyes)}))
