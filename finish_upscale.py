"""Finish upscaled art to 2048 webp game assets.
Usage: finish_upscale.py [--src-dir DIR --assets-dir DIR]
- Opaque ESRGAN outputs (4096) -> Lanczos down to 2048 webp.
- Transparent cutouts -> 2048 webp (downscale if larger, Pillow upscale
  if 1024; ESRGAN never touches alpha).
Defaults: --src-dir from ART_SRC_DIR env (else the staging dir the
intermediates were generated in), --assets-dir defaults to the repo
assets/ dir containing this script (tools/art/../../assets).
"""
import argparse
import os
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--src-dir', default=os.environ.get('ART_SRC_DIR', r'C:\Users\frnd\AppData\Local\Temp\opencode'))
ap.add_argument('--assets-dir', default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')))
a_args = ap.parse_args()

T = a_args.src_dir
R = a_args.assets_dir
TARGET = 2048


def save2048(im, dst):
    w, h = im.size
    if max(w, h) != TARGET:
        s = TARGET / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=88, method=6)
    print('wrote', dst, im.size)


opaque = [
    ('up-classroom.png', 'bg/classroom.webp'),
    ('up-library.png', 'bg/library.webp'),
    ('up-courtyard.png', 'bg/courtyard.webp'),
    ('up-stairwell.png', 'bg/stairwell.webp'),
    ('up-closet.png', 'bg/closet.webp'),
    ('up-sealed.png', 'cg/sealed.webp'),
    ('up-panel.png', 'cg/panel.webp'),
    ('up-panel-alt.png', 'cg/panel-alt.webp'),
    ('up-cover.png', 'cover.webp'),
]
for src, dst in opaque:
    p = os.path.join(T, src)
    if not os.path.exists(p):
        print('MISSING', src)
        continue
    save2048(Image.open(p).convert('RGB'), os.path.join(R, dst))

cuts = [
    ('mio-11d-biref-dc.png', 'cast/mio.webp'),
    ('mio-happy2-cut.png', 'cast/mio-happy.webp'),
    ('mio-x-sad-cut.png', 'cast/mio-sad.webp'),
    ('mio-x-angry-cut.png', 'cast/mio-angry.webp'),
    ('mio-x-blush-cut.png', 'cast/mio-blush.webp'),
    ('renji-21-cut.png', 'cast/renji.webp'),
    ('renji-happy-cut.png', 'cast/renji-happy.webp'),
    ('renji-sad-cut.png', 'cast/renji-sad.webp'),
    ('renji-angry-cut.png', 'cast/renji-angry.webp'),
    ('renji-blush-cut.png', 'cast/renji-blush.webp'),
    ('aoi-line-cut.png', 'cast/aoi.webp'),
    ('aoi-happy-cut.png', 'cast/aoi-happy.webp'),
    ('aoi-sad-cut.png', 'cast/aoi-sad.webp'),
    ('aoi-angry-cut.png', 'cast/aoi-angry.webp'),
    ('aoi-blush-cut.png', 'cast/aoi-blush.webp'),
    ('jan-cut.png', 'cast/janitor.webp'),
    ('janitor-happy-cut.png', 'cast/janitor-happy.webp'),
    ('janitor-sad-cut.png', 'cast/janitor-sad.webp'),
    ('janitor-angry-cut.png', 'cast/janitor-angry.webp'),
    ('janitor-blush-cut.png', 'cast/janitor-blush.webp'),
    ('jan-silhouette.png', 'cast/janitor-silhouette.webp'),
]
for src, dst in cuts:
    p = os.path.join(T, src)
    if not os.path.exists(p):
        print('MISSING', src)
        continue
    save2048(Image.open(p).convert('RGBA'), os.path.join(R, dst))
print('DONE')
