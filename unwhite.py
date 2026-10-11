"""White-background removal by exact unblend (deterministic, preserves wisps/edges).
alpha = 255 - min(R,G,B); foreground color unmixed from white."""
import sys
import numpy as np
from PIL import Image

inn, out = sys.argv[1], sys.argv[2]
img = Image.open(inn).convert('RGB')
a = np.array(img).astype(np.float32)
m = a.min(axis=2)
alpha = 255.0 - m
out_a = np.zeros_like(a)
nz = alpha > 0
out_a[nz] = np.clip((a[nz] - (255.0 - alpha[nz, None])) / (alpha[nz, None] / 255.0), 0, 255)
res = np.dstack([out_a, alpha]).astype(np.uint8)
Image.fromarray(res, 'RGBA').save(out)
print(f'wrote {out}', flush=True)
