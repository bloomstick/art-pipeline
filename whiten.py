"""Whiten a near-uniform background via corner flood-fill.
Usage: whiten.py --inn ... --out ... [--tol 18]
Fills from all four corners (plus edge midpoints) on a downscaled copy for
speed, then applies the mask at full res. Pixels within <tol> per-channel
diff of the corner seeds become pure white.
"""
import argparse
import cv2
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--tol', type=int, default=18)
a = p.parse_args()

img = cv2.imread(a.inn)
h, w = img.shape[:2]
small = cv2.resize(img, (w // 4, h // 4))
sh, sw = small.shape[:2]
mask = np.zeros((sh + 2, sw + 2), np.uint8)
flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY
seeds = [(0, 0), (sw - 1, 0), (0, sh - 1), (sw - 1, sh - 1),
         (sw // 2, 0), (sw // 2, sh - 1), (0, sh // 2), (sw - 1, sh // 2)]
tmp = small.copy()
for x, y in seeds:
    cv2.floodFill(tmp, mask, (x, y), (0, 0, 0),
                  (a.tol,) * 3, (a.tol,) * 3, flags)
filled = mask[1:-1, 1:-1]
full = cv2.resize(filled, (w, h), interpolation=cv2.INTER_NEAREST)
out = img.copy()
out[full > 0] = (255, 255, 255)
n = int((full > 0).sum())
print(f'whitened px: {n} ({n / (w * h) * 100:.1f}%)')
cv2.imwrite(a.out, out)
print(f'wrote {a.out}')
