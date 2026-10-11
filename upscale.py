"""Upscale an image with Pillow (Lanczos). CPU-only, always available."""
import argparse
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--scale', type=float, default=2.0)
a = p.parse_args()

img = Image.open(a.inn).convert('RGB')
w, h = img.size
img.resize((int(w * a.scale), int(h * a.scale)), Image.LANCZOS).save(a.out)
print(f'wrote {a.out}')
