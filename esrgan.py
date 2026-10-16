"""Upscale with Real-ESRGAN x4 (tile-safe for 8GB). CPU-safe on AMD."""
import argparse, os, subprocess, sys

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--model', default=os.environ.get('ART_ESRGAN_MODEL'))
p.add_argument('--tile', type=int, default=0, help='0 = no tiling (required on this box: tile>0 segfaults; 32GB RAM holds full-frame)')
p.add_argument('--device', default='auto', choices=('auto', 'cuda', 'cpu'),
               help='auto: try cuda in a subprocess, fall back to cpu if it dies (segfault-safe)')
a = p.parse_args()
if not a.model:
    sys.exit('ART_ESRGAN_MODEL is not set (RealESRGAN_x4plus.pth path; see docs/MACHINE-SETUP.md)')


def run(device):
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    import cv2
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    up = RealESRGANer(scale=4, model_path=a.model, model=model, tile=a.tile,
                      tile_pad=10, pre_pad=0, half=(device == 'cuda'), device=device)
    img = cv2.imread(a.inn, cv2.IMREAD_UNCHANGED)
    out, _ = up.enhance(img, outscale=4)
    cv2.imwrite(a.out, out)
    print(f'wrote {a.out} via {device}', flush=True)


if a.device in ('cuda', 'cpu'):
    run(a.device)
else:
    # A segfault (e.g. CUDA attempt on AMD, 0xC0000005) kills the process
    # before any try/except can run — so the cuda attempt is quarantined
    # in a subprocess; only its exit code crosses the boundary.
    probe = subprocess.run(
        [sys.executable, os.path.abspath(__file__), '--inn', a.inn, '--out', a.out,
         '--model', a.model, '--tile', str(a.tile), '--device', 'cuda'])
    if probe.returncode == 0 and os.path.exists(a.out):
        print('cuda path held', flush=True)
    else:
        print(f'cuda subprocess died (rc={probe.returncode}); falling back to cpu', flush=True)
        run('cpu')
