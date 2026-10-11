import argparse
import cv2
import numpy as np
p = argparse.ArgumentParser()
p.add_argument('--inn', required=True)
p.add_argument('--out', required=True)
p.add_argument('--box', default='850,950,1024,1024', help='x0,y0,x1,y1')
p.add_argument('--thr', type=int, default=150)
a = p.parse_args()
x0, y0, x1, y1 = map(int, a.box.split(','))
img = cv2.imread(a.inn)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape
zone = np.zeros((h, w), np.uint8)
zone[y0:y1, x0:x1] = 255
text = ((gray > a.thr) & (zone > 0)).astype(np.uint8) * 255
text = cv2.dilate(text, np.ones((3, 3), np.uint8))
print('sig px:', int((text > 0).sum()), flush=True)
cv2.imwrite(a.out, cv2.inpaint(img, text, 6, cv2.INPAINT_TELEA))
print(f'wrote {a.out}', flush=True)
