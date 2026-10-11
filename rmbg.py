"""Remove image background with rembg. Downloads the model (~170MB) on first run."""
import argparse
from rembg import remove, new_session

p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--model', default='birefnet-general')
p.add_argument('--dc', action='store_true',
               help='decontaminate edge colors (cheap halo fix)')
p.add_argument('--am', action='store_true',
               help='alpha matting (slow; fixes mask shape, implies dc)')
a = p.parse_args()

with open(a.inn, 'rb') as f:
    data = f.read()
kwargs = {}
if a.model != 'isnet-general-use' or a.dc or a.am:
    kwargs['session'] = new_session(a.model)
out = remove(data, decontaminate=a.dc, alpha_matting=a.am, **kwargs)
with open(a.out, 'wb') as f:
    f.write(out)
print(f'wrote {a.out} model={a.model} dc={a.dc} am={a.am}')
