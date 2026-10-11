"""Badge with ears popping out: circle crop + ear regions pasted back (deterministic).
Ears = light components touching the circle, in the upper region only.
Usage: pop_ears.py --inn ... --out ... [--cx 514 --cy 492 --r 305 --half 350 --thresh 90]"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--cx', type=int, default=514)
p.add_argument('--cy', type=int, default=492)
p.add_argument('--r', type=int, default=305)
p.add_argument('--half', type=int, default=350)
p.add_argument('--thresh', type=int, default=90)
p.add_argument('--min-size', type=int, default=3000)
a = p.parse_args()

img = cv2.imread(a.inn)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
Y, X = np.ogrid[:h, :w]
circle = (X - a.cx) ** 2 + (Y - a.cy) ** 2 <= a.r ** 2

light = gray > a.thresh
n, lab, stats, _ = cv2.connectedComponentsWithStats(light.astype(np.uint8), 8)
touch = cv2.dilate(circle.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
keep = np.zeros_like(light, dtype=bool)
for i in range(1, n):
    comp = lab == i
    size = stats[i, cv2.CC_STAT_AREA]
    touches = bool((comp & touch).any())
    upper = bool((comp & (Y < a.cy - 50)).any())
    on_border = bool(comp[0, :].any() or comp[-1, :].any() or comp[:, 0].any() or comp[:, -1].any())
    if touches and upper and not on_border and size > a.min_size:
        keep |= comp
        print(f'kept comp size={size}', flush=True)

mask = Image.fromarray(((circle | keep) * 255).astype(np.uint8))
mask = mask.filter(ImageFilter.GaussianBlur(1))
rgba = Image.open(a.inn).convert('RGBA')
rgba.putalpha(mask)
rgba.crop([a.cx - a.half, a.cy - a.half, a.cx + a.half, a.cy + a.half]).save(a.out)
print(f'wrote {a.out}', flush=True)
