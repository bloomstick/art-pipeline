"""Rectangular full-bleed: navy beyond medallion disc + recenter emblem. Deterministic.
Usage: rectify.py --inn ... --out ... [--ecx 1568 --ecy 1488 --r-fill 1500]
Defaults preserve the original e-rect badge run; override per source."""
import argparse
import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--ecx', type=int, default=1568, help='emblem true center x in source px')
p.add_argument('--ecy', type=int, default=1488, help='emblem true center y in source px')
p.add_argument('--r-fill', type=int, default=1500)
p.add_argument('--navy', default='19335A', help='hex RGB beyond disc')
a = p.parse_args()

INN, OUT = a.inn, a.out
ECX, ECY = a.ecx, a.ecy
NAVY = tuple(int(a.navy[i:i + 2], 16) for i in (0, 2, 4))
R_FILL = a.r_fill

img = Image.open(INN).convert('RGB')
W, H = img.size
Y, X = np.ogrid[:H, :W]
arr = np.array(img)
arr[np.hypot(X - ECX, Y - ECY) > R_FILL] = NAVY
img = Image.fromarray(arr)
dx, dy = W // 2 - ECX, H // 2 - ECY
print(f'shift {dx},{dy}', flush=True)
img.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=NAVY).save(OUT)
print(f'wrote {OUT}', flush=True)
