# 일본판 항목 이름 기준 추출: python extract_text2.py jp.fpc us.fpc out.json [추가 북미판 fpc...]
import json, sys
from fpctree import *
from kolib import selt_sites
from selt3 import read_selt
from extract_text import tokenize

jp_fn, us_fn, out_fn, extra = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
def blocks_of(fn):
    t = parse_file(open(fn, 'rb').read())
    return [read_selt(lst.items[k].body.data) for lst, k in selt_sites(t)]
jb, ub = blocks_of(jp_fn), blocks_of(us_fn)
assert len(jb) == len(ub)
pool = {}
for fn in [us_fn] + extra:
    for bl in blocks_of(fn):
        for n, tx in bl: pool.setdefault(n, tx)
out = []; fixed = []
for jbl, ubl in zip(jb, ub):
    umap = {n: tx for n, tx in ubl}
    ents = []
    for i, (n, jtx) in enumerate(jbl):
        tx = umap.get(n)
        if tx is None and i < len(ubl) and ubl[i][0][:8] == n[:8] and n not in pool:
            tx = ubl[i][1]                      # 이름 끝자리(화자)만 다른 경우: 같은 위치
        if tx is None:
            tx = pool.get(n); fixed.append(n)
        assert tx is not None, ('북미판에 없는 항목', n)
        sp, jp = tokenize(tx[0]); _, en = tokenize(tx[1])
        ents.append({'name': n, 'speaker': sp, 'jp': jp, 'en': en, 'ko': ''})
    out.append({'path': [], 'first': ents[0]['name'], 'entries': ents})
json.dump(out, open(out_fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out_fn, [(b['first'], len(b['entries'])) for b in out], '다른 파일에서 채움:', fixed)
