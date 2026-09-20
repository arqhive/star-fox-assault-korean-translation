# 텍스처 한글화 + 일본판 로고의 일본어 부제만 교체 (북미판 불필요)
import json, hashlib
from gcfs import read_fst
from nut import parse_nutc
from gxtex import decode_nut_tex
from texedit import apply_ops, encode_like, tex_key, patch_textures
import texspec, texspec2, texpick
import paths

LOGO_N = 95

def build(disk, out_files):
    cands = json.load(open(paths.DATA / 'texcands.json'))
    fj, *_, ej = read_fst(paths.jp_iso())
    def load(n):
        p, absoff, ti = cands[n]['locs'][0]; fj.seek(absoff); nd = fj.read(0x800000)
        t = parse_nutc(nd)[ti]; return nd, t
    alltex = json.load(open(paths.DATA / 'alltex.json'))      # 전체 고유 텍스처 (GIDX가 달라도 같은 내용이면 모두 교체)
    where = {}
    for c in alltex: where.setdefault((c['w'], c['h'], c['key'][3]), set()).update(l[0] for l in c['locs'])
    repl = {}; touched = set()
    def add(nd, t, ops):
        k = tex_key(nd, t)[1:]
        orig = decode_nut_tex(nd, t)
        repl[k] = encode_like(nd, t, apply_ops(orig, ops), orig)   # 바뀐 부분만 재인코딩
        touched.update(where[k])
    for n, ops in texspec.SPEC.items():
        nd, t = load(n); add(nd, t, ops)
    for ref, ops in texspec2.SPEC2.items():
        nd, t = texpick.load(ref); add(nd, t, ops)
    from build_logo import localize_logo
    nd, t = load(LOGO_N)
    original = decode_nut_tex(nd, t)
    repl[tex_key(nd, t)[1:]] = encode_like(nd, t, localize_logo(original), original)
    touched |= where[tex_key(nd, t)[1:]]
    files = {}; total = 0
    for p in sorted(touched):
        src = out_files.get(p) or disk(p)
        new, n = patch_textures(src, repl); total += n
        if n: files[p] = new
    print('  textures: %d+%d specs + logo, %d replacements in %d files' % (len(texspec.SPEC), len(texspec2.SPEC2), total, len(files)))
    return files
