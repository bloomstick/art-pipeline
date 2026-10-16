import re
import sys
import os
from collections import Counter
REPO = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.environ.get('ART_OUTPUT_DIR', os.path.join(REPO, 'output'))
target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTDIR, 'e10-hd.svg')
s = open(target, encoding='utf-8').read()
fills = re.findall(r'fill="(#[0-9A-Fa-f]{6})"', s)
c = Counter(fills)
print(len(fills), 'colored paths;', len(c), 'colors')
paths = re.findall(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]{6})"', s)
tot = {}
for d, f in paths:
    tot[f] = tot.get(f, 0) + len(d)
for k, v in c.most_common(14):
    print(k, 'n=', v, 'datalen=', tot[k])
