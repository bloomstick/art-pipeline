"""Two-pass refine: img2img polish at low denoise. Usage: refine.py --inn ... --out ... --prompt ... [opts]"""
import argparse, os, json, os, shutil, sys, time, urllib.request

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
INPUT = os.environ.get('COMFY_INPUT')
if not INPUT:
    sys.exit('COMFY_INPUT is not set (ComfyUI input dir; see docs/MACHINE-SETUP.md)')
p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--prompt', required=True)
p.add_argument('--negative', default='')
p.add_argument('--ckpt', default='sd_xl_base_1.0.safetensors')
p.add_argument('--seed', type=int, default=5)
p.add_argument('--steps', type=int, default=15)
p.add_argument('--cfg', type=float, default=7.0)
p.add_argument('--denoise', type=float, default=0.3)
p.add_argument('--sampler', default='dpmpp_2m')
p.add_argument('--scheduler', default='karras')
a = p.parse_args()

name = os.path.basename(a.inn)
shutil.copyfile(a.inn, os.path.join(INPUT, name))
wf = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': a.ckpt}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.prompt, 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.negative, 'clip': ['1', 1]}},
    '4': {'class_type': 'LoadImage', 'inputs': {'image': name}},
    '5': {'class_type': 'VAEEncode', 'inputs': {'pixels': ['4', 0], 'vae': ['1', 2]}},
    '6': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
         'latent_image': ['5', 0], 'seed': a.seed, 'steps': a.steps, 'cfg': a.cfg,
         'sampler_name': a.sampler, 'scheduler': a.scheduler, 'denoise': a.denoise}},
    '7': {'class_type': 'VAEDecode', 'inputs': {'samples': ['6', 0], 'vae': ['1', 2]}},
    '8': {'class_type': 'SaveImage', 'inputs': {'images': ['7', 0], 'filename_prefix': 'refine'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'ref'}).encode(),
                             headers={'content-type': 'application/json'})
pid_ = json.load(urllib.request.urlopen(req, timeout=60))['prompt_id']
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
        urllib.request.urlretrieve(q, a.out)
        print(f'saved {a.out}', flush=True)
        break
else:
    sys.exit('refine timed out')
