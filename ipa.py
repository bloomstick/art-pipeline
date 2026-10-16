"""Style-locked txt2img via IPAdapter (Mio = style anchor).
Usage: ipa.py --prompt ... --out ... --ref mio-11d-raw.png
  [--w 1024 --h 1024 --seed N --weight 0.5 --wtype "style transfer"]
Ref image is copied into the ComfyUI input dir. Requires the IPAdapter
custom node + ipadapter/clip_vision models (see docs/art-pipeline.md).
"""
import argparse, os, json, os, shutil, sys, time, urllib.request

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
INPUT = os.environ.get('COMFY_INPUT')
if not INPUT:
    sys.exit('COMFY_INPUT is not set (ComfyUI input dir; see docs/MACHINE-SETUP.md)')
p = argparse.ArgumentParser()
p.add_argument('--prompt', required=True)
p.add_argument('--negative', default='')
p.add_argument('--ref', required=True, help='reference image path (style anchor)')
p.add_argument('--out', required=True)
p.add_argument('--w', type=int, default=1024)
p.add_argument('--h', type=int, default=1024)
p.add_argument('--seed', type=int, default=68)
p.add_argument('--ckpt', default='animagine-xl-4.0.safetensors')
p.add_argument('--steps', type=int, default=28)
p.add_argument('--cfg', type=float, default=5.0)
p.add_argument('--weight', type=float, default=0.5)
p.add_argument('--wtype', default='style transfer')
a = p.parse_args()

name = os.path.basename(a.ref)
shutil.copyfile(a.ref, os.path.join(INPUT, name))
wf = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': a.ckpt}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.prompt, 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.negative, 'clip': ['1', 1]}},
    '4': {'class_type': 'LoadImage', 'inputs': {'image': name}},
    '5': {'class_type': 'IPAdapterUnifiedLoader',
          'inputs': {'model': ['1', 0], 'preset': 'PLUS (high strength)'}},
    '6': {'class_type': 'IPAdapterAdvanced',
          'inputs': {'model': ['5', 0], 'ipadapter': ['5', 1], 'image': ['4', 0],
                     'weight': a.weight, 'weight_type': a.wtype,
                     'combine_embeds': 'concat', 'start_at': 0.0, 'end_at': 1.0,
                     'embeds_scaling': 'V only'}},
    '7': {'class_type': 'EmptyLatentImage', 'inputs': {'width': a.w, 'height': a.h, 'batch_size': 1}},
    '8': {'class_type': 'KSampler', 'inputs': {'model': ['6', 0], 'positive': ['2', 0], 'negative': ['3', 0],
         'latent_image': ['7', 0], 'seed': a.seed, 'steps': a.steps, 'cfg': a.cfg,
         'sampler_name': 'euler_ancestral', 'scheduler': 'normal', 'denoise': 1.0}},
    '9': {'class_type': 'VAEDecode', 'inputs': {'samples': ['8', 0], 'vae': ['1', 2]}},
    '10': {'class_type': 'SaveImage', 'inputs': {'images': ['9', 0], 'filename_prefix': 'ipa'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'ipa'}).encode(),
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
        imgs = e['outputs']['10']['images']
        q = f"{COMFY}/view?filename={imgs[0]['filename']}&subfolder={imgs[0].get('subfolder','')}&type={imgs[0].get('type','output')}"
        urllib.request.urlretrieve(q, a.out)
        print(f'saved {a.out}', flush=True)
        break
else:
    sys.exit('ipa timed out')
