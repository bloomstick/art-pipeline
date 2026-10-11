import re
import sys
from collections import Counter
target = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\frnd\AppData\Local\Temp\opencode\e10-hd.svg'
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
