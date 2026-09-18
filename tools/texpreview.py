import sys, numpy as np
from PIL import Image, ImageDraw
from texview import load
from texedit import apply_ops, encode_like
from gxtex import decode_nut_tex
import importlib, texspec
def show(nums, out):
    tiles = []
    for n in nums:
        nd, t, img = load(n)
        new = apply_ops(img, texspec.SPEC[n])
        enc = encode_like(nd, t, new); nd2 = bytearray(nd); nd2[t['data_off']:t['data_off'] + t['dsz']] = enc
        dec = decode_nut_tex(bytes(nd2), t)      # 실제 인코딩 결과
        sc = 3 if max(t['w'], t['h']) <= 160 else 2
        row = []
        for im in (img, dec):
            p = Image.fromarray(im); bg = Image.new('RGBA', p.size, (90, 60, 120, 255)); bg.alpha_composite(p)
            row.append(bg.resize((t['w'] * sc, t['h'] * sc), Image.NEAREST))
        cv = Image.new('RGB', (row[0].width * 2 + 40, row[0].height + 16), (20, 20, 20)); dr = ImageDraw.Draw(cv)
        cv.paste(row[0], (0, 14)); cv.paste(row[1], (row[0].width + 40, 14)); dr.text((2, 0), '#%d' % n, fill=(0, 255, 255))
        tiles.append(cv)
    W = max(t.width for t in tiles); H = sum(t.height + 4 for t in tiles)
    sheet = Image.new('RGB', (W, H)); y = 0
    for t in tiles: sheet.paste(t, (0, y)); y += t.height + 4
    sheet.save(out)
if __name__ == '__main__':
    show([int(x) for x in sys.argv[2:]], sys.argv[1])
