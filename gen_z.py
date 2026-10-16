"""Seed-locked Z-Image-Turbo int8 submitter. ALWAYS embeds the UI workflow.

Usage: gen_z.py --prompt TEXT --out FILE [--negative TEXT] [--seed N]
       [--prefix NAME] [--w 1024 --h 1024]

Single source of truth: reference/z-image-turbo-int8/workflow.json.
This script patches the template (positive/negative/seed/size/prefix),
derives the API prompt from the SAME values, and posts
extra_data.extra_pnginfo.workflow so outputs are one-click reloadable.
Raw API-only submissions are banned (docs/COMFYUI-OPS.md sec 6).
Portable: COMFY_URL + ART_PIPELINE_DIR (template path) only.
"""
import argparse, copy, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.environ.get('ART_PIPELINE_DIR', HERE),
                        'reference', 'z-image-turbo-int8', 'workflow.json')
COMFY = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188')

NEG_DEFAULT = ("lowres, bad anatomy, bad hands, missing finger, extra digits, "
               "fewer digits, cropped, worst quality, deformed face, deformed eyes, "
               "asymmetrical eyes, crossed eyes, ugly face, watermark, text, "
               "duplicate limbs, ghost limbs, extra arms, fused fingers")

p = argparse.ArgumentParser()
p.add_argument('--prompt', required=True)
p.add_argument('--out', required=True)
p.add_argument('--negative', default=NEG_DEFAULT)
p.add_argument('--seed', type=int, required=True)
p.add_argument('--prefix', default='genz')
p.add_argument('--w', type=int, default=1024)
p.add_argument('--h', type=int, default=1024)
a = p.parse_args()

with open(TEMPLATE, encoding='utf-8') as f:
    ui = json.load(f)

by_id = {n['id']: n for n in ui['nodes']}


def set_widgets(node_id, values):
    by_id[node_id]['widgets_values'] = values


set_widgets(67, [a.prompt])
set_widgets(71, [a.negative])
ks = list(by_id[70]['widgets_values'])
ks[0] = a.seed
set_widgets(70, ks)
lat = list(by_id[68]['widgets_values'])
lat[0], lat[1] = a.w, a.h
set_widgets(68, lat)
set_widgets(9, [a.prefix])

api = {
 '66': {'class_type': 'UNETLoader', 'inputs': {
     'unet_name': by_id[66]['widgets_values'][0],
     'weight_dtype': by_id[66]['widgets_values'][1]}},
 '62': {'class_type': 'CLIPLoader', 'inputs': {
     'clip_name': by_id[62]['widgets_values'][0],
     'type': by_id[62]['widgets_values'][1],
     'device': by_id[62]['widgets_values'][2]}},
 '63': {'class_type': 'VAELoader', 'inputs': {
     'vae_name': by_id[63]['widgets_values'][0]}},
 '67': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.prompt, 'clip': ['62', 0]}},
 '71': {'class_type': 'CLIPTextEncode', 'inputs': {'text': a.negative, 'clip': ['62', 0]}},
 '68': {'class_type': 'EmptySD3LatentImage', 'inputs': {'width': a.w, 'height': a.h, 'batch_size': 1}},
 '69': {'class_type': 'ModelSamplingAuraFlow', 'inputs': {'model': ['66', 0], 'shift': 3.0}},
 '70': {'class_type': 'KSampler', 'inputs': {'model': ['69', 0], 'positive': ['67', 0],
      'negative': ['71', 0], 'latent_image': ['68', 0], 'seed': a.seed,
      'steps': 8, 'cfg': 1.0, 'sampler_name': 'res_multistep',
      'scheduler': 'simple', 'denoise': 1.0}},
 '65': {'class_type': 'VAEDecode', 'inputs': {'samples': ['70', 0], 'vae': ['63', 0]}},
 '9': {'class_type': 'SaveImage', 'inputs': {'images': ['65', 0], 'filename_prefix': a.prefix}},
}
body = {'prompt': api, 'client_id': 'genz',
        'extra_data': {'extra_pnginfo': {'workflow': ui}}}
req = urllib.request.Request(COMFY + '/prompt', data=json.dumps(body).encode(),
                             headers={'content-type': 'application/json'})
pid_ = json.load(urllib.request.urlopen(req, timeout=60))['prompt_id']
print('prompt_id', pid_, flush=True)
sidecar = os.path.splitext(a.out)[0] + '.workflow.json'
with open(sidecar, 'w', encoding='utf-8') as f:
    json.dump(ui, f)
print('sidecar', sidecar, flush=True)
t0 = time.time()
while time.time() - t0 < 1500:
    time.sleep(10)
    try:
        hist = json.load(urllib.request.urlopen(COMFY + '/history/' + pid_, timeout=30))
    except Exception as e:
        print('hist-wait', ascii(e), flush=True)
        continue
    e = hist.get(pid_)
    if e and e.get('status', {}).get('completed'):
        imgs = e['outputs']['9']['images']
        q = COMFY + '/view?filename=' + imgs[0]['filename'] + '&subfolder=' + \
            imgs[0].get('subfolder', '') + '&type=' + imgs[0].get('type', 'output')
        urllib.request.urlretrieve(q, a.out)
        print(f'saved {a.out} in {round(time.time() - t0)}s (workflow embedded)', flush=True)
        sys.exit(0)
sys.exit('generation timed out')
