"""Upscale via ComfyUI ESRGAN node. Usage: cupscale.py --inn ... --out ... [--model RealESRGAN_x4plus.pth]"""
import argparse, os, json, os, shutil, sys, time, urllib.request

COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')
INPUT = os.environ.get('COMFY_INPUT', r'C:\comfyui-rocm\input')
p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--model', default='RealESRGAN_x4plus.pth')
a = p.parse_args()

name = os.path.basename(a.inn)
shutil.copyfile(a.inn, os.path.join(INPUT, name))
wf = {
    '1': {'class_type': 'LoadImage', 'inputs': {'image': name}},
    '2': {'class_type': 'UpscaleModelLoader', 'inputs': {'model_name': a.model}},
    '3': {'class_type': 'ImageUpscaleWithModel', 'inputs': {'upscale_model': ['2', 0], 'image': ['1', 0]}},
    '4': {'class_type': 'SaveImage', 'inputs': {'images': ['3', 0], 'filename_prefix': 'up'}},
}
req = urllib.request.Request(f'{COMFY}/prompt', data=json.dumps({'prompt': wf, 'client_id': 'cup'}).encode(),
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
        imgs = e['outputs']['4']['images']
        q = f"{COMFY}/view?filename={imgs[0]['filename']}&subfolder={imgs[0].get('subfolder','')}&type={imgs[0].get('type','output')}"
        urllib.request.urlretrieve(q, a.out)
        print(f'saved {a.out}', flush=True)
        break
else:
    sys.exit('upscale timed out')
