import json, sys, numpy as np
from PIL import Image, ImageDraw
from gcfs import read_fst
from nut import parse_nutc
from gxtex import decode_nut_tex
c = json.load(open('texcands.json'))
f, *_, e = read_fst('../Star Fox - Assault (Japan).iso')
def load(n):
    p, absoff, ti = c[n]['locs'][0]; f.seek(absoff); nd = f.read(0x200000); t = parse_nutc(nd)[ti]
    return nd, t, decode_nut_tex(nd, t)
if __name__ == '__main__':
    nums = [int(x) for x in sys.argv[2:]]; out = sys.argv[1]
    tiles = []
    for n in nums:
        nd, t, img = load(n)
        sc = 3 if max(t['w'], t['h']) <= 200 else 2
        im = Image.fromarray(img); bg = Image.new('RGBA', im.size, (255, 0, 255, 255)); bg.alpha_composite(im)
        im = bg.resize((t['w'] * sc, t['h'] * sc), Image.NEAREST)
        cv = Image.new('RGB', (im.width + 30, im.height + 30), (30, 30, 30)); cv.paste(im, (30, 30)); dr = ImageDraw.Draw(cv)
        for x in range(0, t['w'] + 1, 8):
            dr.line([(30 + x * sc, 26), (30 + x * sc, 30)], fill=(255, 255, 0))
            if x % 40 == 0: dr.text((30 + x * sc, 12), str(x), fill=(255, 255, 0))
        for y in range(0, t['h'] + 1, 8):
            dr.line([(26, 30 + y * sc), (30, 30 + y * sc)], fill=(255, 255, 0))
            if y % 40 == 0 or t['h'] <= 48: dr.text((2, 30 + y * sc - 5), str(y), fill=(255, 255, 0))
        dr.text((2, 2), '#%d' % n, fill=(0, 255, 255))
        tiles.append(cv)
    W = max(t.width for t in tiles); H = sum(t.height + 6 for t in tiles)
    sheet = Image.new('RGB', (W, H), (0, 0, 0)); y = 0
    for t in tiles: sheet.paste(t, (0, y)); y += t.height + 6
    sheet.save(out); print(out, sheet.size)
