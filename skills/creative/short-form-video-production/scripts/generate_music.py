#!/usr/bin/env python3
"""Инструментал для рилса: тёплые пэды, бас, мягкий бит, колокольчик. Без вокала и сэмплов.
48 кГц стерео WAV. usage: generate_music.py out.wav [seconds] [bpm]
Печатает метрики приёмки: пик, RMS, баланс спектра, стерео-корреляцию."""
import numpy as np, sys, os, wave

OUT = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 10.5
BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 92.0
SR = 48000
N = int(DUR * SR)
beat = 60.0 / BPM
bar = beat * 4
rng = np.random.default_rng(11)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


prog = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67]]   # Am - F - C - G
L = np.zeros(N)
R = np.zeros(N)

# ---- пэды: пила в три детюна, НЧ-фильтр по основной массе + нефильтрованный «воздух» ----
for ci, ch in enumerate(prog):
    start = int(ci * bar * SR)
    if start >= N:
        break
    length = int(bar * 1.15 * SR)
    base = np.zeros(length)
    air = np.zeros(length)
    for note in ch:
        for det in (-0.14, 0.0, 0.14):
            ph = 2 * np.pi * hz(note + det) * np.arange(length) / SR + rng.uniform(0, 6.28)
            saw = 2 * (ph / (2 * np.pi) % 1.0) - 1.0
            base += saw
            air += saw * 0.12
    a = 0.10
    lp = np.zeros_like(base)
    acc = 0.0
    for i in range(length):
        acc += a * (base[i] - acc)
        lp[i] = acc
    env = np.minimum(1.0, np.arange(length) / (0.30 * SR))
    env *= np.minimum(1.0, (length - np.arange(length)) / (0.55 * SR))
    seg = (lp * 0.34 + air * 0.22) * env
    end = min(N, start + length)
    d = int(0.009 * SR)                       # Haas-сдвиг: ширина без фазовой грязи
    L[start:end] += seg[:end - start]
    if end + d <= N:
        R[start + d:end + d] += seg[:end - start] * 0.92
    else:
        R[start:end] += seg[:end - start] * 0.92

# ---- бас ----
for ci, ch in enumerate(prog):
    for half in range(2):
        start = int((ci * bar + half * beat * 2) * SR)
        if start >= N:
            break
        length = int(beat * 1.6 * SR)
        f0 = hz(ch[0] - 12)
        seg = np.sin(2 * np.pi * f0 * np.arange(length) / SR) * 0.20
        seg += 0.06 * np.sin(2 * np.pi * f0 * 2 * np.arange(length) / SR)
        seg *= np.exp(-np.arange(length) / (0.5 * SR))
        end = min(N, start + length)
        L[start:end] += seg[:end - start]
        R[start:end] += seg[:end - start]

# ---- бочка на 1 и 3 ----
kl = int(0.26 * SR)
K = np.sin(2 * np.pi * np.cumsum(np.linspace(115, 46, kl)) / SR) * np.exp(-np.arange(kl) / (0.055 * SR)) * 0.42
for b in range(int(DUR / beat) + 1):
    if b % 4 not in (0, 2):
        continue
    s = int(b * beat * SR)
    if s + kl > N:
        break
    L[s:s + kl] += K
    R[s:s + kl] += K

# ---- хэты с панорамой ----
hl = int(0.05 * SR)
for h in range(int(DUR / (beat / 2)) + 1):
    s = int(h * (beat / 2) * SR)
    if s + hl > N:
        break
    n = rng.normal(0, 1, hl) * np.exp(-np.arange(hl) / (0.010 * SR))
    n = np.diff(np.concatenate([[0], n, [0]]))[:hl]
    amp = 0.17 if h % 2 else 0.10
    pan = 0.62 if h % 2 else 0.38
    L[s:s + hl] += n * amp * (1 - pan) * 1.7
    R[s:s + hl] += n * amp * pan * 1.7

# ---- колокольчик по пентатонике ----
pent = [69, 72, 74, 76, 79, 81]
for k in range(16):
    s = int((0.45 + k * 0.63) * SR)
    if s >= N:
        break
    ln = int(1.0 * SR)
    f0 = hz(pent[rng.integers(0, len(pent))] + 12)
    ar = np.arange(ln)
    seg = (np.sin(2 * np.pi * f0 * ar / SR) * 0.20
           + np.sin(2 * np.pi * f0 * 2.01 * ar / SR) * 0.07
           + np.sin(2 * np.pi * f0 * 3.02 * ar / SR) * 0.03)
    seg *= np.exp(-ar / (0.24 * SR))
    end = min(N, s + ln)
    pan = rng.uniform(0.25, 0.75)
    L[s:end] += seg[:end - s] * (1 - pan) * 2.0
    R[s:end] += seg[:end - s] * pan * 2.0

# ---- воздух: очень тихий ВЧ-шум, в каналах со сдвигом ----
airn = rng.normal(0, 1, N)
airn = np.diff(np.concatenate([[0], airn, [0]]))[:N]
L += airn * 0.006
R += np.roll(airn, 197) * 0.006


def reverb(x, taps, gains):
    y = x.copy()
    for tap, g in zip(taps, gains):
        d = int(tap * SR)
        if d < len(x):
            y[d:] += x[:-d] * g
    return y


L = reverb(L, (0.071, 0.137, 0.211, 0.293, 0.379), (0.20, 0.15, 0.11, 0.07, 0.04))
R = reverb(R, (0.083, 0.149, 0.223, 0.307, 0.401), (0.20, 0.15, 0.11, 0.07, 0.04))

fi, fo = int(0.08 * SR), int(1.2 * SR)
ramp = np.linspace(0, 1, fi)
L[:fi] *= ramp
R[:fi] *= ramp
out = np.linspace(1, 0, fo) ** 1.4
L[-fo:] *= out
R[-fo:] *= out

mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.15) / 1.15
mix = mix / np.abs(mix).max() * 0.89
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())

# ---- отчёт приёмки ----
mono = mix.mean(axis=1)
sp = np.abs(np.fft.rfft(mono))
fr = np.fft.rfftfreq(len(mono), 1 / SR)
total = sp[(fr >= 20) & (fr < 20000)].sum()
print(f"готово: {OUT} ({os.path.getsize(OUT)/1e6:.2f} МБ)")
print(f"  {DUR:.2f} с, {BPM:.0f} BPM, пик {20*np.log10(np.abs(mix).max()):.1f} dBFS, "
      f"RMS {20*np.log10(np.sqrt((mix**2).mean())):.1f} dBFS (цель -14…-10)")
for lo, hi, name in [(20, 120, 'низ'), (120, 800, 'низ-середина'), (800, 3000, 'середина'),
                     (3000, 9000, 'верх'), (9000, 20000, 'воздух')]:
    part = sp[(fr >= lo) & (fr < hi)].sum()
    print(f"    {name:14} {part/total*100:5.1f}%")
print(f"  стерео-корреляция: {np.corrcoef(mix[:,0], mix[:,1])[0,1]:.2f} (1.0 = моно, цель 0.3–0.6)")
