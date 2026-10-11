"""Circular crop with transparent outside. Usage: crop_circle.py --inn ... --out ... [--cx 512 --cy 512 --r 470]"""
import argparse
from PIL import Image, ImageDraw, ImageFilter

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--cx', type=int, default=512)
p.add_argument('--cy', type=int, default=512)
p.add_argument('--r', type=int, default=470)
p.add_argument('--feather', type=int, default=0)
a = p.parse_args()

img = Image.open(a.inn).convert('RGBA')
mask = Image.new('L', img.size, 0)
ImageDraw.Draw(mask).ellipse([a.cx - a.r, a.cy - a.r, a.cx + a.r, a.cy + a.r], fill=255)
if a.feather:
    mask = mask.filter(ImageFilter.GaussianBlur(a.feather))
img.putalpha(mask)
img.crop([a.cx - a.r, a.cy - a.r, a.cx + a.r, a.cy + a.r]).save(a.out)
print(f'wrote {a.out}', flush=True)
