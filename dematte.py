"""Closed-form alpha matting refinement. Usage: dematte.py --inn <rgba> --out <rgba> [--rad 7]"""
import argparse
import cv2
import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--rad', type=int, default=7)
a = p.parse_args()

from pymatting import estimate_alpha_cf, estimate_foreground_ml

img = Image.open(a.inn).convert('RGBA')
arr = np.array(img).astype(np.float64) / 255.0
rgb, alpha = arr[:, :, :3], arr[:, :, 3]
k = np.ones((3, 3), np.uint8)
fg = cv2.erode((alpha > 0.78).astype(np.uint8), k, iterations=a.rad) > 0
bg = cv2.dilate((alpha < 0.02).astype(np.uint8), k, iterations=a.rad) > 0
trimap = np.full_like(alpha, 0.5)
trimap[fg] = 1.0
trimap[bg] = 0.0
print('trimap unknown frac:', round(float(((trimap > 0) & (trimap < 1)).mean()), 4), flush=True)
na = estimate_alpha_cf(rgb, trimap)
nf = estimate_foreground_ml(rgb, na)
out = np.dstack([np.clip(nf, 0, 1), na])
Image.fromarray((out * 255).astype(np.uint8)).save(a.out)
print(f'wrote {a.out}', flush=True)
