import sys
import numpy as np
from PIL import Image
inn, out = sys.argv[1], sys.argv[2]
thr = int(sys.argv[3]) if len(sys.argv) > 3 else 190
sat = int(sys.argv[4]) if len(sys.argv) > 4 else 25
alph = float(sys.argv[5]) if len(sys.argv) > 5 else 0.2
im = np.array(Image.open(inn))
H, W, _ = im.shape
Y, X = np.ogrid[:H, :W]
R = np.hypot(X - W // 2, Y - H // 2)
c = im[:, :, :3].astype(int)
mx, mn = c.max(axis=2), c.min(axis=2)
m = (mn > thr) & ((mx - mn) < sat) & (R > 1300)
print('attenuated px:', int(m.sum()), flush=True)
im[:, :, 3] = (im[:, :, 3].astype(float) * np.where(m, alph, 1)).astype(np.uint8)
Image.fromarray(im).save(out)
print(f'wrote {out}', flush=True)
