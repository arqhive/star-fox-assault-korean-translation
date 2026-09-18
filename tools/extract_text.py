# 미션 fpc에서 번역용 JSON 추출: 일본어(북미판 lang0 SJIS), 영어(북미판 lang1)
import json, sys
from fpctree import *
from selt3 import read_selt

def tokenize(w, keep_ruby=False):
    """코드열 → 번역용 문자열. 화자 헤더는 분리, 루비 제거, 아이콘은 {xxxx:n} 토큰"""
    speaker = None
    if w and (w[0] >> 16) == 0xA000:
        speaker = w[0] & 0xFFFF
        w = w[1:]
        if w and w[0] == 0xFFFFFFFF: w = w[1:]
    out = []
    for v in w:
        if v == 0xFFFFFFFF: out.append('\n'); continue
        fl, c = v >> 16, v & 0xFFFF
        if fl == 0xC000:
            out.append(chr(c >> 8) if c & 0xFF == 0 else bytes([c >> 8, c & 0xFF]).decode('shift_jis', 'replace'))
        elif 0x40 <= (fl >> 8) <= 0x4F and (fl & 0xFF) == 0x08:
            if keep_ruby: out.append('{%04x:%d}' % (fl, c))
        else:
            out.append('{%04x:%d}' % (fl, c))
    return speaker, ''.join(out)

def selt_blocks(t):
    return [(p, it) for p, it in walk(t) if not it.empty and isinstance(it.body, Leaf) and it.body.data[:4] == b'SELT']

if __name__ == '__main__':
    us_fn, out_fn = sys.argv[1], sys.argv[2]
    t = parse_file(open(us_fn, 'rb').read())
    blocks = []
    for p, it in selt_blocks(t):
        ents = []
        for nm, texts in read_selt(it.body.data):
            sp, jp = tokenize(texts[0])
            sp2, en = tokenize(texts[1])
            ents.append({'name': nm, 'speaker': sp, 'jp': jp, 'en': en, 'ko': ''})
        blocks.append({'path': [str(x) for x in p], 'first': ents[0]['name'], 'entries': ents})
    json.dump(blocks, open(out_fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(out_fn, [(b['first'], len(b['entries'])) for b in blocks])
