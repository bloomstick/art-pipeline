"""CPU smoke test: wait for ComfyUI, run SDXL-Turbo 512px job, save result."""
import json, os, sys, time, urllib.request

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
REPO = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.environ.get('ART_OUTPUT_DIR', os.path.join(REPO, 'output'))
os.makedirs(OUTDIR, exist_ok=True)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTDIR, 'smoke.png')

for _ in range(60):
    try:
        urllib.request.urlopen(f'{COMFY}/system_stats', timeout=5)
        break
    except Exception:
        time.sleep(5)
else:
    sys.exit('server not up')

wf = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': 'sd_xl_turbo_1.0_fp16.safetensors'}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': 'a cute robot mascot head, flat vector badge style', 'clip': ['1', 1]}},
    '3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': '', 'clip': ['1', 1]}},
    '4': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 512, 'height': 512, 'batch_size': 1}},
    '5': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
         'latent_image': ['4', 0], 'seed': 42, 'steps': 4, 'cfg': 1.5,
         'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0}},
    '6': {'class_type': 'VAEDecode', 'inputs': {'samples': ['5', 0], 'vae': ['1', 2]}},
    '7': {'class_type': 'SaveImage', 'inputs': {'images': ['6', 0], 'filename_prefix': 'smoke'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'smoke'}).encode(),
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
        urllib.request.urlretrieve(q, OUT)
        print(f'saved {OUT}', flush=True)
        break
else:
    sys.exit('generation timed out')
