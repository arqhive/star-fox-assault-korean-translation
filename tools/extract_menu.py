# c000(SJIS 폰트) 방식 파일 추출: 일본어는 일본판, 영어는 북미판 같은 이름
import json, sys, collections
from kolib import *
from extract_text import tokenize
jp_fn, us_fn, out_fn = sys.argv[1:4]
def blocks(fn):
    t = parse_file(open(fn, 'rb').read()); return [read_selt(l.items[k].body.data) for l, k in selt_sites(t)]
jb, ub = blocks(jp_fn), blocks(us_fn)
codes = collections.Counter(); out = []
for jbl, ubl in zip(jb, ub):
    um = {n: tx for n, tx in ubl}; ents = []
    for n, tx in jbl:
        for v in tx[0]:
            if v != 0xFFFFFFFF: codes['%04x' % (v >> 16)] += 1
        sp, jp = tokenize(tx[0])
        en = tokenize(um[n][1])[1] if n in um else ''
        ents.append({'name': n, 'speaker': sp, 'jp': jp, 'en': en, 'ko': ''})
    out.append({'path': [], 'first': ents[0]['name'], 'entries': ents})
json.dump(out, open(out_fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out_fn, [(b['first'], len(b['entries'])) for b in out], dict(codes))
