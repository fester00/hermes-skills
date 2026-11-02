#!/usr/bin/env python3
"""Грейд кадра из линейного RAW: экспозиция/WB/BGR в линейном,
фильмическая кривая, шумодав в тенях, лица, clarity, вибранс, винъетка, шарп.

usage: grade_scene.py in16.npy out.jpg [scale] ['{json params}']
   in16.npy  — uint16 linear RGB из rawpy (см. references/raw-and-grading.md)
   scale     — 0.3 для итераций, 1.0 для финала
"""
import numpy as np, cv2, sys, json

SRC = sys.argv[1]
DST = sys.argv[2]
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
P = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}

rgb = np.load(SRC)
H, W = rgb.shape[:2]
if SCALE != 1.0:
    rgb = cv2.resize(rgb, (int(W * SCALE), int(H * SCALE)), interpolation=cv2.INTER_AREA)
h, w = rgb.shape[:2]

x = rgb.astype(np.float32) / 65535.0
x *= 2 ** P.get('ev', 0.35)                      # экспозиция в линейном

# --- баланс белого по нейтральным светлым пикселям ---
L0 = x.mean(axis=2)
neutral = (L0 > 0.35) & (L0 < 0.92)
if neutral.sum() > 5000:
    m = np.array([x[:, :, c][neutral].mean() for c in range(3)], np.float32)
    tgt = m.mean()
    x *= 1.0 + (tgt / np.maximum(m, 1e-6) - 1.0) * P.get('wb', 0.85)

# --- фильмическая кривая (мягкие света, плотные тени) ---
def filmic(v, black=0.008, white=0.93, contrast=1.0):
    v = np.clip((v - black) / (white - black), 0, 1)
    v = (v * (2.51 * v + 0.03)) / (v * (2.43 * v + 0.59) + 0.14)
    return np.clip((v - 0.5) * contrast + 0.5, 0, 1)

x = filmic(x, black=P.get('black', 0.008), white=P.get('white', 0.93),
           contrast=P.get('contrast', 1.06))


def lin2srgb(v):
    return np.where(v <= 0.0031308, v * 12.92,
                    1.055 * np.power(np.maximum(v, 1e-8), 1 / 2.4) - 0.055)


img = (lin2srgb(np.clip(x, 0, 1)) * 255).astype(np.uint8)
# КРИТИЧНО: rawpy отдаёт RGB, весь конвейер ниже — BGR
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# --- шумодав только в тенях ---
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
Lc = lab[:, :, 0]
shadow = np.clip((0.45 - Lc / 255.0) / 0.45, 0, 1) ** 0.8
a = cv2.bilateralFilter(lab[:, :, 1], 7, 22, 7)
b = cv2.bilateralFilter(lab[:, :, 2], 7, 22, 7)
k = P.get('chroma_dn', 0.85) * shadow
lab[:, :, 1] = lab[:, :, 1] * (1 - k) + a * k
lab[:, :, 2] = lab[:, :, 2] * (1 - k) + b * k
Ldn = cv2.bilateralFilter(lab[:, :, 0], 5, 18, 5)
kl = P.get('luma_dn', 0.6) * shadow
lab[:, :, 0] = lab[:, :, 0] * (1 - kl) + Ldn * kl
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# --- тени / света ---
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0] / 255.0
L = L + P.get('shadow_lift', 0.09) * (1 - L) ** 2.2
L = L - P.get('hl_roll', 0.12) * np.clip(L - 0.75, 0, 1) ** 1.2
lab[:, :, 0] = np.clip(L, 0, 1) * 255
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# --- маска кожи и лица ---
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
Cr, Cb, Y = ycrcb[:, :, 1], ycrcb[:, :, 2], ycrcb[:, :, 0]
sk = ((Cr > 135) & (Cr < 180) & (Cb > 80) & (Cb < 130) & (Y > 50)).astype(np.uint8)
sk = cv2.morphologyEx(sk, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
sk = cv2.GaussianBlur(sk * 255.0, (0, 0), max(1.0, w * 0.004)) / 255.0
skin = np.clip(sk * 1.1, 0, 1)[..., None]

lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
softL = cv2.cvtColor(cv2.bilateralFilter(img, 9, 26, 9), cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
amt = P.get('face_smooth', 0.35)
L = L * (1 - amt * skin[..., 0]) + softL * (amt * skin[..., 0])
L = L + P.get('face_lift', 10.0) * skin[..., 0]
lab[:, :, 0] = np.clip(L, 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# --- локальный контраст ---
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
base = cv2.GaussianBlur(L, (0, 0), max(2.0, w * 0.012))
lab[:, :, 0] = np.clip(L + P.get('clarity', 0.30) * (L - base), 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# --- вибранс + акцент в красном ---
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
S = hsv[:, :, 1]
hsv[:, :, 1] = np.clip(S * (1 + P.get('vibrance', 0.20) * (1 - S / 255.0) + P.get('sat_base', 0.02)), 0, 255)
img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
lab[:, :, 1] = np.clip(lab[:, :, 1] + P.get('red_acc', 2.0), 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

# --- винъетка ---
yy, xx = np.mgrid[0:h, 0:w]
d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
vig = 1 - P.get('vignette', 0.14) * np.clip(d - 0.65, 0, 1.3) ** 1.5
img = np.clip(img.astype(np.float32) * vig[..., None], 0, 255).astype(np.uint8)

# --- резкость, гашение на коже ---
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
hi = L - cv2.GaussianBlur(L, (0, 0), max(1.0, w * 0.0006))
lab[:, :, 0] = np.clip(L + P.get('sharpen', 0.40) * hi * (1 - 0.6 * skin[..., 0]), 0, 255)
img = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

cv2.imwrite(DST, img, [int(cv2.IMWRITE_JPEG_QUALITY), int(P.get('quality', 95))])
print(json.dumps({'out': DST, 'size': [int(w), int(h)]}))
