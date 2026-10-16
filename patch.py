"""Surgical patch: crop region -> img2img repaint -> feathered paste-back (RGB only, alpha kept)."""
import argparse, json, os, shutil, sys, time, urllib.request
import cv2
import numpy as np
from PIL import Image, ImageFilter

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
INPUT = os.environ.get('COMFY_INPUT')
if not INPUT:
    sys.exit('COMFY_INPUT is not set (ComfyUI input dir; see docs/MACHINE-SETUP.md)')
p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--box', required=True, help='x0,y0,x1,y1 in source px')
p.add_argument('--prompt', required=True)
p.add_argument('--negative', default='')
p.add_argument('--ckpt', default='animagine-xl-4.0.safetensors')
p.add_argument('--seed', type=int, default=77)
p.add_argument('--steps', type=int, default=24)
p.add_argument('--cfg', type=float, default=5.0)
p.add_argument('--denoise', type=float, default=0.55)
p.add_argument('--sampler', default='euler_ancestral')
p.add_argument('--size', type=int, default=1024)
p.add_argument('--feather', type=int, default=90)
a = p.parse_args()

x0, y0, x1, y1 = map(int, a.box.split(','))
src = Image.open(a.inn).convert('RGB')
crop = src.crop((x0, y0, x1, y1))
crop_orig = crop.copy()
crop = crop.resize((a.size, a.size), Image.LANCZOS)
cname = f'patch_{os.getpid()}.png'
crop.save(os.path.join(INPUT, cname))
sx = (x1 - x0) / a.size
sy = (y1 - y0) / a.size
wf = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': a.ckpt}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.prompt, 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.negative, 'clip': ['1', 1]}},
    '4': {'class_type': 'LoadImage', 'inputs': {'image': cname}},
    '5': {'class_type': 'VAEEncode', 'inputs': {'pixels': ['4', 0], 'vae': ['1', 2]}},
    '6': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
         'latent_image': ['5', 0], 'seed': a.seed, 'steps': a.steps, 'cfg': a.cfg,
         'sampler_name': a.sampler, 'scheduler': 'normal', 'denoise': a.denoise}},
    '7': {'class_type': 'VAEDecode', 'inputs': {'samples': ['6', 0], 'vae': ['1', 2]}},
    '8': {'class_type': 'SaveImage', 'inputs': {'images': ['7', 0], 'filename_prefix': 'patch'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'patch'}).encode(),
                             headers={'content-type': 'application/json'})
pid_ = json.load(urllib.request.urlopen(req, timeout=120))['prompt_id']
print('prompt_id', pid_, flush=True)
for _ in range(120):
    time.sleep(5)
    try:
        hist = json.load(urllib.request.urlopen(f'{COMFY}/history/{pid_}', timeout=30))
    except Exception:
        continue
    e = hist.get(pid_)
    if e and e.get('status', {}).get('completed'):
        imgs = e['outputs']['8']['images']
        q = f"{COMFY}/view?filename={imgs[0]['filename']}&subfolder={imgs[0].get('subfolder','')}&type={imgs[0].get('type','output')}"
        tmp = a.out + '.new.png'
        urllib.request.urlretrieve(q, tmp)
        new = Image.open(tmp).convert('RGB').resize((x1 - x0, y1 - y0), Image.LANCZOS)
        na, nb = np.array(new).astype(np.float32), np.array(crop).astype(np.float32)
        ma, sa = na.mean((0, 1)), na.std((0, 1)) + 1e-6
        mb, sb = nb.mean((0, 1)), nb.std((0, 1))
        new = Image.fromarray(np.clip((na - ma) / sa * sb + mb, 0, 255).astype(np.uint8))
        m = Image.new('L', (x1 - x0, y1 - y0), 0)
        from PIL import ImageDraw
        ImageDraw.Draw(m).rounded_rectangle([0, 0, x1 - x0, y1 - y0], radius=a.feather * 2, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(a.feather // 2))
        cb = np.array(crop_orig).astype(int)
        cmx, cmn = cb.max(axis=2), cb.min(axis=2)
        keepbg = ((cmx - cmn) < 70) & (cmn > 150)
        keepbg = Image.fromarray((keepbg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30))
        m = Image.fromarray(np.minimum(np.array(m).astype(np.float32),
                                       255 - np.array(keepbg).astype(np.float32)).astype(np.uint8))
        base = Image.open(a.inn).convert('RGBA')
        base.paste(new, (x0, y0), m)
        base.save(a.out)
        print(f'saved {a.out}', flush=True)
        break
else:
    sys.exit('patch timed out')
