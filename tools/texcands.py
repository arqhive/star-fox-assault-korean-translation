import json, hashlib, numpy as np
from PIL import Image, ImageDraw
from gcfs import read_fst
import paths
from nut import parse_nutc
from gxtex import decode_nut_tex
diff = {(k[0], k[1], k[2], k[3]) for k, v in json.load(open('texdiff.json'))}
miss = {tuple(k) for k in json.load(open('texmissing.json')) if not k[0].startswith('/attract/')}
want = diff | miss
f, *_, e = read_fst(paths.jp_iso())
cands = {}   # hash -> info
for p, o, s in e:
    if p not in {k[0] for k in want}: continue
    f.seek(o); d = f.read(s); i = -1; k = 0
    while True:
        i = d.find(b'NUTC', i + 1)
        if i < 0: break
        try: ts = parse_nutc(d[i:])
        except Exception: continue
        for t in ts:
            gid = d[i+t['off']+0x48:i+t['off']+0x4C].hex()
            if (p, gid, t['w'], t['h']) not in want: continue
            blob = d[i+t['data_off']:i+t['data_off']+t['dsz']] + d[i+t['pal_off']:i+t['pal_off']+t['pal']]
            h = hashlib.md5(blob).hexdigest()
            info = cands.setdefault(h, dict(hash=h, fmt=t['fmt'], w=t['w'], h=t['h'], gid=gid, locs=[]))
            info['locs'].append([p, o + i, t['i']])
            if 'img' not in info:
                try:
                    img = decode_nut_tex(d[i:], t)
                    if img is not None: info['img'] = img
                except Exception as ex: info['err'] = str(ex)
        k += 1
lst = sorted(cands.values(), key=lambda c: (c['locs'][0][0], -c['w']*c['h']))
print('unique candidates', len(lst), 'undecoded', sum(1 for c in lst if 'img' not in c), set(c['fmt'] for c in lst if 'img' not in c))
# 모음 이미지: 한 장에 폭 1000px
pages = []; x = y = rowh = 0; page = Image.new('RGBA', (1000, 1400), (60, 60, 90, 255)); dr = ImageDraw.Draw(page)
for n, c in enumerate(lst):
    c['n'] = n
    if 'img' not in c: continue
    im = Image.fromarray(c['img']); sc = 1
    if im.width > 480: sc = 480 / im.width
    if im.height * sc > 240: sc = 240 / im.height
    if sc != 1: im = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))))
    if x + im.width + 4 > 1000: x = 0; y += rowh + 16; rowh = 0
    if y + im.height + 16 > 1400:
        pages.append(page); page = Image.new('RGBA', (1000, 1400), (60, 60, 90, 255)); dr = ImageDraw.Draw(page); x = y = rowh = 0
    page.alpha_composite(im, (x, y + 12)); dr.text((x, y), str(n), fill=(255, 255, 0, 255))
    x += im.width + 8; rowh = max(rowh, im.height)
pages.append(page)
for k, pg in enumerate(pages): pg.save(f'cand_{k}.png')
json.dump([{kk: vv for kk, vv in c.items() if kk != 'img'} for c in lst], open('texcands.json', 'w'), indent=0)
print('pages', len(pages))
