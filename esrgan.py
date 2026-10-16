"""Upscale with Real-ESRGAN x4 (tile-safe for 8GB). Falls back to CPU on GPU failure."""
import argparse, os, sys

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--model', default=os.environ.get('ART_ESRGAN_MODEL'))
p.add_argument('--tile', type=int, default=128)
a = p.parse_args()
if not a.model:
    sys.exit('ART_ESRGAN_MODEL is not set (RealESRGAN_x4plus.pth path; see docs/MACHINE-SETUP.md)')

from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import numpy as np, cv2

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
for device in ('cuda', 'cpu'):
    try:
        up = RealESRGANer(scale=4, model_path=a.model, model=model, tile=a.tile,
                           tile_pad=10, pre_pad=0, half=(device == 'cuda'), device=device)
        img = cv2.imread(a.inn, cv2.IMREAD_UNCHANGED)
        out, _ = up.enhance(img, outscale=4)
        cv2.imwrite(a.out, out)
        print(f'wrote {a.out} via {device}', flush=True)
        break
    except Exception as e:
        print(f'{device} failed: {e}', flush=True)
else:
    sys.exit('both devices failed')
