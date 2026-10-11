"""Radial badge finish: keep interior, flat navy annulus, exactly two gold circles, transparent outside.
Usage: finish_v2.py --inn ... --out ... (tunable radii/widths)"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--cx', type=int, default=514)
p.add_argument('--cy', type=int, default=492)
p.add_argument('--r-blue', type=int, default=335)
p.add_argument('--r-out', type=int, default=362)
p.add_argument('--ring1', type=int, default=350)
p.add_argument('--w1', type=int, default=6)
p.add_argument('--ring2', type=int, default=360)
p.add_argument('--w2', type=int, default=3)
p.add_argument('--gold', default='C9A227')
p.add_argument('--half', type=int, default=375)
a = p.parse_args()

bgr = cv2.imread(a.inn)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
Y, X = np.ogrid[:h, :w]
R = np.sqrt((X - a.cx) ** 2 + (Y - a.cy) ** 2)

b, g, rr = bgr[:, :, 0].astype(int), bgr[:, :, 1].astype(int), bgr[:, :, 2].astype(int)
is_blue = (b - rr > 20) & (b - g > 10) & (gray < 110)
navy = np.median(bgr[is_blue], axis=0)[::-1].astype(np.uint8)  # RGB
print(f'navy sample: {tuple(navy)}', flush=True)

img = Image.open(a.inn).convert('RGBA')
px = img.load()
nv = tuple(int(v) for v in navy)
band = (R >= a.r_blue) & (R < a.r_out)
ys, xs = np.where(band)
for x, y in zip(xs.tolist(), ys.tolist()):
    px[x, y] = nv + (255,)

mask = Image.new('L', img.size, 0)
ImageDraw.Draw(mask).ellipse([a.cx - a.r_out, a.cy - a.r_out, a.cx + a.r_out, a.cy + a.r_out], fill=255)
img.putalpha(mask.filter(ImageFilter.GaussianBlur(1)))
badge = img.crop([a.cx - a.half, a.cy - a.half, a.cx + a.half, a.cy + a.half])

d = ImageDraw.Draw(badge, 'RGBA')
gold = tuple(int(a.gold[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
cx = cy = a.half
for r, wd in ((a.ring1, a.w1), (a.ring2, a.w2)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=gold, width=wd)
badge.save(a.out)
print(f'wrote {a.out} size={badge.size}', flush=True)
