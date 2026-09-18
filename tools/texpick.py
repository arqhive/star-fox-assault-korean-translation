# 스캔 결과에서 텍스처 로드: ('A',17) → (nd, t) / (w,h,md5)
import json
from gcfs import read_fst
from nut import parse_nutc
from texedit import tex_key
_f = None; _scans = {}
def _iso():
    global _f
    if _f is None: _f = read_fst('../Star Fox - Assault (Japan).iso')[0]
    return _f
def loc_of(ref):
    s, n = ref
    if s not in _scans: _scans[s] = json.load(open('scan%s.json' % s))
    c = _scans[s][n]
    if 'locs' in c: p, a, ti = c.get('loc') or c['locs'][0]
    else: p, a, ti = c['path'], c['abs'], c['ti']
    return p, a, ti
def load(ref):
    p, a, ti = loc_of(ref); f = _iso(); f.seek(a); nd = f.read(0x1000000)
    return nd, parse_nutc(nd)[ti]
