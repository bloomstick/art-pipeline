import sys
import numpy as np
from PIL import Image

inn, out = sys.argv[1], sys.argv[2]
im = Image.open(inn).convert('RGBA')
a = np.array(im)
opaque = float((a[..., 3] > 250).mean()) * 100
semi = float(((a[..., 3] > 10) & (a[..., 3] <= 250)).mean()) * 100
print('size', im.size, 'opaque%', round(opaque, 1), 'semi%', round(semi, 2))
bg = Image.new('RGBA', im.size, (255, 0, 255, 255))
bg.alpha_composite(im)
bg.convert('RGB').save(out)
print('wrote', out)
