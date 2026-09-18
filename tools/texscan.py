import json, sys, hashlib, numpy as np
from PIL import Image, ImageDraw
from gcfs import read_fst
from nut import parse_nutc
from gxtex import decode_nut_tex
from texedit import tex_key
import texspec
files = sys.argv[2:]; out = sys.argv[1]
cands = json.load(open('texcands.json'))
done = {c['hash'] for n, c in enumerate(cands) if n in texspec.SPEC or n == 95}
f, *_, e = read_fst('../Star Fox - Assault (Japan).iso'); loc = {p: (o, s) for p, o, s in e}
found = {}
for p in files:
    o, s = loc[p]; f.seek(o); d = f.read(s); i = -1
    while True:
        i = d.find(b'NUTC', i + 1)
        if i < 0: break
        try: ts = parse_nutc(d[i:])
        except Exception: continue
        for t in ts:
            if t['fmt'] not in (4, 5, 6) or t['h'] > 64 or t['w'] < 24 or t['h'] < 8: continue
            k = tex_key(d[i:], t)
            if k[3] in done or k in found: continue
            try: img = decode_nut_tex(d[i:], t)
            except Exception: continue
            if img is None: continue
            found[k] = dict(path=p, abs=o + i, ti=t['i'], img=img, w=t['w'], h=t['h'], fmt=t['fmt'])
lst = list(found.values())
pages = []; x = y = rowh = 0; W, H = 1000, 1400
page = Image.new('RGBA', (W, H), (70, 50, 100, 255)); dr = ImageDraw.Draw(page)
for n, c in enumerate(lst):
    im = Image.fromarray(c['img']); sc = 2 if c['w'] <= 240 else 1
    im = im.resize((c['w'] * sc, c['h'] * sc), Image.NEAREST)
    if x + im.width + 30 > W: x = 0; y += rowh + 14; rowh = 0
    if y + im.height + 14 > H:
        pages.append(page); page = Image.new('RGBA', (W, H), (70, 50, 100, 255)); dr = ImageDraw.Draw(page); x = y = rowh = 0
    page.alpha_composite(im, (x, y + 12)); dr.text((x, y), str(n), fill=(255, 255, 0, 255))
    x += im.width + 10; rowh = max(rowh, im.height)
pages.append(page)
for k, pg in enumerate(pages): pg.save('%s_%d.png' % (out, k))
json.dump([{kk: vv for kk, vv in c.items() if kk != 'img'} for c in lst], open(out + '.json', 'w'))
print(len(lst), 'textures,', len(pages), 'pages')
