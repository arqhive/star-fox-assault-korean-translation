# 한글화한 텍스처 자체 점검: 재압축 잡티 / 지운 글자 자국 / 반투명 가장자리
#   python tools/texqa.py            (문제 많은 순으로 출력)
import json, sys
import numpy as np
import paths, texspec, texspec2, texpick
from gcfs import read_fst
from nut import parse_nutc
from gxtex import decode_nut_tex
from texedit import apply_ops, encode_like

import cv2

def analyze(o, new, enc):
    """o=원본, new=편집 목표, enc=인코딩 후 실제 결과"""
    lum = lambda im: im[..., :3].astype(int).mean(-1)
    untouched = (o == new).all(-1)
    noise = int((untouched & (np.abs(enc.astype(int) - o.astype(int)).max(-1) > 8)).sum())
    # 글자(원문·한글)에서 2px 이상 떨어진 '배경'이 얼마나 깨끗한지: 원본과 비교
    base = np.median(lum(o))
    was_text = np.abs(lum(o) - base) > 40
    now_text = np.abs(lum(new) - base) > 40
    far = ~cv2.dilate((was_text | now_text).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    dirty_new = int((far & (np.abs(lum(enc) - base) > 12)).sum())
    dirty_old = int((far & (np.abs(lum(o) - base) > 12)).sum())
    ghost = max(0, dirty_new - dirty_old)     # 원본에도 있던 무늬는 빼고 센다
    a = enc[..., 3]
    semi = int(((a > 8) & (a < 247)).sum())
    return noise, ghost, semi, o.shape[0] * o.shape[1]

def main():
    cands = json.load(open(paths.DATA / 'texcands.json'))
    f, *_, e = read_fst(paths.jp_iso())
    rows = []
    for n, ops in sorted(texspec.SPEC.items()):
        p, a, ti = cands[n]['locs'][0]; f.seek(a); nd = f.read(0x800000); t = parse_nutc(nd)[ti]
        rows.append((str(n), nd, t, ops))
    for ref, ops in texspec2.SPEC2.items():
        nd, t = texpick.load(ref); rows.append(('%s%d' % ref, nd, t, ops))
    out = []
    for name, nd, t, ops in rows:
        o = decode_nut_tex(nd, t); new = apply_ops(o, ops)
        b = bytearray(nd); b[t['data_off']:t['data_off'] + t['dsz']] = encode_like(nd, t, new, o)
        enc = decode_nut_tex(bytes(b), t)
        noise, ghost, semi, px = analyze(o, new, enc)
        out.append((noise + ghost * 2, name, t['fmt'], t['w'], t['h'], noise, ghost, semi, px))
    out.sort(reverse=True)
    print('%-6s %-4s %-9s %8s %8s %10s' % ('이름', 'fmt', '크기', '재압축잡티', '배경얼룩', '반투명픽셀'))
    for score, name, fmt, w, h, noise, ghost, semi, px in out:
        if score == 0 and semi * 100 // px < 10: continue
        print('%-6s %-4d %-9s %8d %8d %9d (%d%%)' % (name, fmt, '%dx%d' % (w, h), noise, ghost, semi, semi * 100 // px))
    print('\n검사한 텍스처 %d개 / 문제 있는 것 %d개' % (len(out), sum(1 for r in out if r[0] > 0)))

if __name__ == '__main__':
    main()
