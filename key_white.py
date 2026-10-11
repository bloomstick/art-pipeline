"""White-bg keying via border flood-fill + unblended edge band. Deterministic."""
import sys
import cv2
import numpy as np
from PIL import Image

inn, out = sys.argv[1], sys.argv[2]
thr = int(sys.argv[3]) if len(sys.argv) > 3 else 238
img = Image.open(inn).convert('RGB')
a = np.array(img).astype(np.float32)
H, W, _ = a.shape
nearwhite = a.min(axis=2) > thr
n, lab, _, _ = cv2.connectedComponentsWithStats(nearwhite.astype(np.uint8), 8)
border_labels = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border_labels))
k = np.ones((3, 3), np.uint8)
band = (cv2.dilate(bg.astype(np.uint8), k) - cv2.erode(bg.astype(np.uint8), k)) > 0
alpha = np.where(bg, 0.0, 255.0)
m = a.min(axis=2)
au = 255.0 - m
ub = np.zeros_like(a)
nz = au > 0
ub[nz] = np.clip((a[nz] - (255.0 - au[nz, None])) / (au[nz, None] / 255.0), 0, 255)
alpha = np.where(band & ~bg, au, alpha)
res = np.dstack([np.where(band[..., None] & ~bg[..., None], ub, a), alpha]).astype(np.uint8)
Image.fromarray(res, 'RGBA').save(out)
print(f'wrote {out} bgfrac={bg.mean():.3f}', flush=True)
