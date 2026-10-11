"""e5 cleanup: medallion + ears/face kept, thin web strands + band arcs removed, navy surround.
Deterministic: connectivity + thickness + color rules, no generative steps.
Scale-aware: pass 4x morphology/threshold values for HD sources."""
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
p.add_argument('--r-paint', type=int, default=300)
p.add_argument('--r-mask', type=int, default=365)
p.add_argument('--half', type=int, default=375)
p.add_argument('--thresh', type=int, default=90)
p.add_argument('--r-red', type=int, default=335)
p.add_argument('--dilate', type=int, default=7)
p.add_argument('--open-k', type=int, default=3)
p.add_argument('--open-i', type=int, default=2)
p.add_argument('--min-cat', type=int, default=3000)
p.add_argument('--min-red', type=int, default=800)
p.add_argument('--feather', type=float, default=1.5)
p.add_argument('--sat', type=int, default=100)
a = p.parse_args()

bgr = cv2.imread(a.inn)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
Y, X = np.ogrid[:h, :w]
R = np.sqrt((X - a.cx) ** 2 + (Y - a.cy) ** 2)
circle = R <= a.r

b, g, rr = bgr[:, :, 0].astype(int), bgr[:, :, 1].astype(int), bgr[:, :, 2].astype(int)
mx = bgr.max(axis=2).astype(int)
mn = bgr.min(axis=2).astype(int)
gold = (rr > 150) & (g > 100) & (b < 130)

light = gray > a.thresh
n, lab, stats, _ = cv2.connectedComponentsWithStats(light.astype(np.uint8), 8)
touch = cv2.dilate(circle.astype(np.uint8), np.ones((a.dilate, a.dilate), np.uint8)) > 0
cat = np.zeros_like(light, dtype=bool)
for i in range(1, n):
    comp = lab == i
    if ((comp & touch).any() and ((comp & (Y < a.cy - 50)).any())
            and not (comp[0, :].any() or comp[-1, :].any() or comp[:, 0].any() or comp[:, -1].any())
            and stats[i, cv2.CC_STAT_AREA] > a.min_cat):
        cat |= comp
print(f'cat px: {cat.sum()}', flush=True)

red = (rr > 110) & (rr - g > 45) & (rr - b > 45)
n2, lab2, stats2, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8), 8)
for i in range(1, n2):
    comp = lab2 == i
    if ((comp & touch).any() and stats2[i, cv2.CC_STAT_AREA] > a.min_red
            and not (comp[0, :].any() or comp[-1, :].any() or comp[:, 0].any() or comp[:, -1].any())):
        near = comp & (R < a.r_red)
        cat |= near
        print(f'red px added: {near.sum()}', flush=True)

ann = (R > a.r) & (R < a.r_mask)
thick = cv2.morphologyEx((cat & ann).astype(np.uint8), cv2.MORPH_OPEN,
                         np.ones((a.open_k, a.open_k), np.uint8), iterations=a.open_i) > 0
thick = thick & ~(ann & gold)
keep = circle | (cat & ~ann) | thick

is_blue = (b - rr > 20) & (b - g > 10) & (gray < 110)
navy = np.median(bgr[is_blue], axis=0)[::-1].astype(np.uint8)

img = Image.open(a.inn).convert('RGBA')
nv = tuple(int(v) for v in navy) + (255,)
paint = (~keep) & (R >= a.r_paint) & (R < a.r_mask)
arr = np.array(img)
arr[paint] = nv
img = Image.fromarray(arr)

mask = Image.new('L', img.size, 0)
ImageDraw.Draw(mask).ellipse([a.cx - a.r_mask, a.cy - a.r_mask, a.cx + a.r_mask, a.cy + a.r_mask], fill=255)
img.putalpha(mask.filter(ImageFilter.GaussianBlur(a.feather)))
img.crop([a.cx - a.half, a.cy - a.half, a.cx + a.half, a.cy + a.half]).save(a.out)
print(f'wrote {a.out}', flush=True)
