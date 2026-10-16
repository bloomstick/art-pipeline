"""Embed a UI workflow chunk into a PNG (backfill for API-only outputs).

Usage: embed_workflow.py --png FILE --prompt TEXT --seed N --prefix NAME
       [--negative TEXT] [--template PATH]

Patches reference/z-image-turbo-int8/workflow.json with the exact values,
writes a <png-basename>.workflow.json sidecar, and re-saves the PNG with
the `workflow` text chunk ADDED — all existing chunks (incl. `prompt`)
preserved, pixels untouched (lossless re-save).
Companion to extract-workflow.py. Portable: ART_PIPELINE_DIR for template.
"""
import argparse, copy, json, os
from PIL import Image
from PIL.PngImagePlugin import PngInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TEMPLATE = os.path.join(
    os.environ.get('ART_PIPELINE_DIR', HERE),
    'reference', 'z-image-turbo-int8', 'workflow.json')

p = argparse.ArgumentParser()
p.add_argument('--png', required=True)
p.add_argument('--prompt', required=True)
p.add_argument('--seed', type=int, required=True)
p.add_argument('--prefix', required=True)
p.add_argument('--negative', default=None)
p.add_argument('--template', default=DEFAULT_TEMPLATE)
a = p.parse_args()

with open(a.template, encoding='utf-8') as f:
    ui = json.load(f)
by_id = {n['id']: n for n in ui['nodes']}
by_id[67]['widgets_values'] = [a.prompt]
if a.negative is not None:
    by_id[71]['widgets_values'] = [a.negative]
ks = list(by_id[70]['widgets_values'])
ks[0] = a.seed
by_id[70]['widgets_values'] = ks
by_id[9]['widgets_values'] = [a.prefix]
wf_text = json.dumps(ui)

base, _ = os.path.splitext(a.png)
sidecar = base + '.workflow.json'
with open(sidecar, 'w', encoding='utf-8') as f:
    f.write(wf_text)
print('sidecar', sidecar)

im = Image.open(a.png)
meta = PngInfo()
for k, v in (im.info or {}).items():
    if isinstance(v, str):
        meta.add_text(k, v)
meta.add_text('workflow', wf_text)
im.save(a.png, pnginfo=meta)
print('embedded workflow into', a.png)
im2 = Image.open(a.png)
print('chunks now:', sorted(im2.info.keys()))
assert 'workflow' in im2.info and 'prompt' in im2.info, 'embed FAILED'
print('OK: prompt + workflow both present')
