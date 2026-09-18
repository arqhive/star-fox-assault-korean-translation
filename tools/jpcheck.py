# 일본어 직역투 후보 찾기: python tools/jpcheck.py [파일이름…]
# 번역문에서 흔한 번역투 패턴을 찾아 원문(work/src)과 함께 보여준다. 판단은 사람이 한다.
import json, re, sys, os, glob
import paths

PATTERNS = [
    ('이 내가/이 몸',      r'이 (내가|나는|나를|몸[의은이]|몸,)'),
    ('~하는 것이다',       r'(하는|라는|인|이라는|된다는) (것이다|것이야|거다|것입니다)'),
    ('~해 버렸다',         r'[가-힣] 버(렸|려|린|릴)'),
    ('~하고 있다',         r'[가-힣]고 (있다|있어|있습니다|있었다)\.?$'),
    ('~에 대해/있어서',    r'에 (대해서?|있어서|관해서?)'),
    ('~로서의',            r'로서의'),
    ('대명사 남발',        r'(그녀|당신|그들)'),
    ('~라니/~하다니',      r'[가-힣](라니|다니)[…!?.]*$'),
    ('과연/역시/제대로',   r'(과연|제대로|확실히|어떻게든|무려)'),
    ('~할 수밖에',         r'할 수밖에'),
    ('~인 거지/~란 말이야', r'(인 거[지야]|란 말[이야]|라는 거[지야])'),
    ('~되어 있다',         r'되어 (있|져)'),
    ('~하는 중이다',       r'하는 중(이|입)'),
    ('수동 직역',          r'(구원받|발견되|파괴되어|공격당하고)'),
    ('일본식 한자어',      r'(본망|고저차|단차|폭풍|에너지량|사념|기체 손상|전의 상실|절체절명|일발|호기|귀환길)'),
    ('~하지 않으면 안',    r'하지 않으면 안'),
    ('~인 것 같다 중복',   r'것 같[다아은]. *것 같'),
    ('~해 주었으면',       r'주었으면'),
    ('들 남발',            r'(우리들|너희들|저희들|녀석들이 나)'),
    ('~라고 할까',         r'라고 할까'),
]

def load_src():
    src = {}
    for fn in glob.glob(str(paths.WORK / 'src' / '*.json')):
        b = json.load(open(fn, encoding='utf-8'))
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl['entries']: src.setdefault(e['name'], e.get('jp', ''))
    return src

def main(names):
    src = load_src()
    files = [paths.KO / (n + '.json') for n in names] if names else sorted(paths.KO.glob('*.json'))
    hits = {}
    for path in files:
        b = json.load(open(path, encoding='utf-8'))
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl['entries']:
                ko = e.get('ko') or ''
                for label, pat in PATTERNS:
                    if re.search(pat, ko):
                        hits.setdefault(label, []).append((path.stem, e['name'], ko, src.get(e['name'], '')))
    total = 0
    for label, pat in PATTERNS:
        rows = hits.get(label, [])
        if not rows: continue
        seen = set(); uniq = []
        for r in rows:
            if (r[1], r[2]) in seen: continue
            seen.add((r[1], r[2])); uniq.append(r)
        total += len(uniq)
        print('\n== %s (%d줄)' % (label, len(uniq)))
        for f, name, ko, jp in uniq:
            print('  %-6s %-14s %s' % (f, name, ko.replace('\n', '/')))
            if jp: print('         원문: %s' % jp.replace('\n', '/'))
    print('\n합계 %d줄' % total)

if __name__ == '__main__':
    main(sys.argv[1:])
