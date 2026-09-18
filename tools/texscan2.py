# ISO 전체 고유 텍스처 중 글자 가능성 있는 것 → 접촉 시트 (이미 본 것 제외)
import json, sys, numpy as np
from PIL import Image, ImageDraw
from gcfs import read_fst
from nut import parse_nutc
from gxtex import decode_nut_tex
import texspec
cands = json.load(open('texcands.json'))
done = {c['hash'] for n, c in enumerate(cands) if n in texspec.SPEC or n == 95}
seen = set()
for sj in ('scanA.json', 'scanB.json'):
    for c in json.load(open(sj)):
        if c['fmt'] in (4, 5): seen.add((c['abs'], c['ti']))
allt = json.load(open('alltex.json'))
f, *_, e = read_fst('../Star Fox - Assault (Japan).iso')
sel = []
for c in allt:
    w, h, fm = c['w'], c['h'], c['fmt']
    if c['key'][3] in done or fm not in (4, 5, 6): continue
    if any((a, ti) in seen for _, a, ti in c['locs']): continue
    if w < 24 or h < 8 or w > 512 or h > 512: continue
    if not (h <= 64 or max(w, h) >= 2 * min(w, h)): continue
    sel.append(c)
print(len(sel))
out = []; pages = []; x = y = rowh = 0; W, H = 1000, 1400
page = Image.new('RGBA', (W, H), (70, 50, 100, 255)); dr = ImageDraw.Draw(page)
cache = {}
for c in sel:
    p, a, ti = c['locs'][0]
    if a not in cache:
        f.seek(a); cache.clear(); cache[a] = f.read(0x1000000)
    nd = cache[a]; t = parse_nutc(nd)[ti]
    try: img = decode_nut_tex(nd, t)
    except Exception: continue
    if img is None or img[..., 3].max() == 0: continue
    im = Image.fromarray(img)
    if im.width > 480: im = im.resize((im.width // 2, im.height // 2))
    elif im.width <= 160 and im.height <= 64: im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    if x + im.width + 10 > W: x = 0; y += rowh + 14; rowh = 0
    if y + im.height + 14 > H:
        pages.append(page); page = Image.new('RGBA', (W, H), (70, 50, 100, 255)); dr = ImageDraw.Draw(page); x = y = rowh = 0
    n = len(out); out.append(c)
    page.alpha_composite(im, (x, y + 12)); dr.text((x, y), str(n), fill=(255, 255, 0, 255))
    x += im.width + 10; rowh = max(rowh, im.height)
pages.append(page)
for k, pg in enumerate(pages): pg.save('scanC_%d.png' % k)
json.dump(out, open('scanC.json', 'w'))
print(len(out), 'textures', len(pages), 'pages')
