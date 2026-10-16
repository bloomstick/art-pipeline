"""Cutout verification: magenta composite + JSON pixel audit.

Paste the image onto (255,0,255) — previews show RGB through transparency,
so ONLY the magenta composite counts — then report a pixel census (alpha +
color counts beat eyeballing downscaled previews).

Usage: verify.py --inn IN.png --out OUT_magenta.png
Prints one JSON line: {w,h,has_alpha,transparent_pct,magenta_visible_pct,
near_white_pct}. Exit 0 on success.

Ported from project-FATHER tools/comfy/verify.py (sole FATHER-side image
tool with own logic; retired there 2026-10-16 consolidation). CLI/JSON
contract unchanged.
"""
import argparse
import json

from PIL import Image

MAGENTA = (255, 0, 255)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--inn', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()

    img = Image.open(a.inn).convert('RGBA')
    w, h = img.size
    n = w * h
    alpha = list(img.getdata(3))
    transparent = sum(1 for v in alpha if v == 0)
    bg = Image.new('RGBA', (w, h), MAGENTA + (255,))
    comp = Image.alpha_composite(bg, img).convert('RGB')
    comp.save(a.out)

    px = list(comp.getdata())
    magenta_visible = sum(1 for r, g, b in px
                          if (r, g, b) == MAGENTA)
    near_white = sum(1 for r, g, b in px
                     if r > 245 and g > 245 and b > 245)
    print(json.dumps({
        'w': w, 'h': h,
        'has_alpha': img.mode == 'RGBA' and transparent > 0,
        'transparent_pct': round(100.0 * transparent / n, 3),
        'magenta_visible_pct': round(100.0 * magenta_visible / n, 3),
        'near_white_pct': round(100.0 * near_white / n, 3),
    }))


if __name__ == '__main__':
    main()
