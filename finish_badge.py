"""Deterministic badge finishing: detect emblem ring, crop centered, crisp vector-drawn border.
Usage: finish_badge.py --inn ... --out ... [--margin 30 --border 10 --color C9A227]"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--margin', type=int, default=30)
p.add_argument('--border', type=int, default=10)
p.add_argument('--color', default='C9A227')
a = p.parse_args()

gray = cv2.imread(a.inn, cv2.IMREAD_GRAYSCALE)
gray = cv2.medianBlur(gray, 5)
h, w = gray.shape
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 400,
                           param1=120, param2=90, minRadius=300, maxRadius=520)
assert circles is not None, 'no ring detected'
cx, cy, r = sorted(circles[0], key=lambda c: abs(c[0] - w / 2) + abs(c[1] - h / 2))[0]
cx, cy, r = int(cx), int(cy), int(r)
print(f'ring center=({cx},{cy}) r={r}', flush=True)

img = Image.open(a.inn).convert('RGBA')
R = r - a.margin
mask = Image.new('L', img.size, 0)
ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1))
img.putalpha(mask)
badge = img.crop([cx - R, cy - R, cx + R, cy + R])

d = ImageDraw.Draw(badge, 'RGBA')
rgb = tuple(int(a.color[i:i + 2], 16) for i in (0, 2, 4))
d.ellipse([a.border // 2, a.border // 2, 2 * R - a.border // 2, 2 * R - a.border // 2],
          outline=rgb + (255,), width=a.border)
badge.save(a.out)
print(f'wrote {a.out} size={badge.size}', flush=True)
