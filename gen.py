"""Generate one image via ComfyUI and save to OUT. Usage: gen.py --prompt ... --out ... [--w 1024 --h 1024 --seed N --ckpt ... --steps 4]"""
import argparse, os, json, sys, time, urllib.request

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
p = argparse.ArgumentParser()
p.add_argument('--prompt', required=True)
p.add_argument('--negative', default='')
p.add_argument('--out', required=True)
p.add_argument('--w', type=int, default=1024)
p.add_argument('--h', type=int, default=1024)
p.add_argument('--seed', type=int, default=1234)
p.add_argument('--ckpt', default='sd_xl_turbo_1.0_fp16.safetensors')
p.add_argument('--steps', type=int, default=4)
p.add_argument('--cfg', type=float, default=1.5)
p.add_argument('--sampler', default='euler')
p.add_argument('--scheduler', default='normal')
a = p.parse_args()

wf = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': a.ckpt}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.prompt, 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.negative, 'clip': ['1', 1]}},
    '4': {'class_type': 'EmptyLatentImage', 'inputs': {'width': a.w, 'height': a.h, 'batch_size': 1}},
    '5': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
         'latent_image': ['4', 0], 'seed': a.seed, 'steps': a.steps, 'cfg': a.cfg,
         'sampler_name': a.sampler, 'scheduler': a.scheduler, 'denoise': 1.0}},
    '6': {'class_type': 'VAEDecode', 'inputs': {'samples': ['5', 0], 'vae': ['1', 2]}},
    '7': {'class_type': 'SaveImage', 'inputs': {'images': ['6', 0], 'filename_prefix': 'opencode'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'gen'}).encode(),
                             headers={'content-type': 'application/json'})
pid_ = json.load(urllib.request.urlopen(req, timeout=60))['prompt_id']
print('prompt_id', pid_, flush=True)
for _ in range(360):
    time.sleep(5)
    try:
        hist = json.load(urllib.request.urlopen(f'{COMFY}/history/{pid_}', timeout=30))
    except Exception:
        continue
    e = hist.get(pid_)
    if e and e.get('status', {}).get('completed'):
        imgs = e['outputs']['7']['images']
        q = f"{COMFY}/view?filename={imgs[0]['filename']}&subfolder={imgs[0].get('subfolder','')}&type={imgs[0].get('type','output')}"
        urllib.request.urlretrieve(q, a.out)
        print(f'saved {a.out}', flush=True)
        break
else:
    sys.exit('generation timed out')
