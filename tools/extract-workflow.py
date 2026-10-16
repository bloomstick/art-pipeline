"""Extract embedded ComfyUI workflows from PNGs and save them as JSON.

Usage:
  python tools/extract-workflow.py <png> [<png> ...] [--outdir DIR]

For each PNG with embedded `prompt` metadata: prints a one-line summary
(checkpoint, sampler, steps, CFG, seed, size) and, with --outdir, saves the
full API workflow JSON beside it as <name>.png.json.
Raw ComfyUI outputs always carry this metadata; re-exported/optimized files
usually don't (keys empty -> reported, not an error).
"""
import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("need Pillow: pip install Pillow")


def summarize(prompt):
    ks = {}
    for v in prompt.values():
        ct = v.get('class_type', '')
        if 'Checkpoint' in ct:
            ks['ckpt'] = v['inputs'].get('ckpt_name')
        if ct == 'KSampler':
            i = v['inputs']
            ks.update(seed=i.get('seed'), steps=i.get('steps'),
                      cfg=i.get('cfg'), sampler=i.get('sampler_name'),
                      sched=i.get('scheduler'))
        if ct == 'EmptyLatentImage':
            ks['size'] = str(v['inputs'].get('width')) + 'x' + str(v['inputs'].get('height'))
        if ct == 'CLIPTextEncode':
            ks.setdefault('prompts', []).append(v['inputs'].get('text', ''))
    return ks


def main(files, outdir):
    for p in files:
        im = Image.open(p)
        meta = im.info.get('prompt')
        name = os.path.basename(p)
        if not meta:
            print(name, im.size, 'NO-META')
            continue
        pr = json.loads(meta)
        ks = summarize(pr)
        print(name, im.size, '|', ks.get('ckpt'), '|', ks.get('sampler'),
              ks.get('sched'), ks.get('steps'), 'cfg', ks.get('cfg'),
              'seed', ks.get('seed'), '|', ks.get('size'))
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            with open(os.path.join(outdir, name + '.json'), 'w') as f:
                json.dump(pr, f, indent=1)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--outdir')]
    outdir = None
    for a in sys.argv[1:]:
        if a.startswith('--outdir='):
            outdir = a.split('=', 1)[1]
    if not args:
        sys.exit(__doc__)
    main(args, outdir)
