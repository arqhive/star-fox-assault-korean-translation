# 번역 변경 내역 비교: python tools/diff_ko.py <이전 폴더> [파일이름…]
import json, sys, os
import paths

def load(p):
    b = json.load(open(p, encoding='utf-8'))
    return {e['name']: e['ko'] for bl in (b if isinstance(b, list) else [b]) for e in bl['entries']}

old_dir = sys.argv[1] if len(sys.argv) > 1 else str(paths.WORK / 'ko_before_review')
names = sys.argv[2:] or sorted(p.stem for p in paths.KO.glob('*.json'))
total = 0
for n in names:
    op = os.path.join(old_dir, n + '.json')
    if not os.path.exists(op): continue
    old, new = load(op), load(paths.KO / (n + '.json'))
    ch = [(k, old[k], new[k]) for k in new if k in old and old[k] != new[k]]
    if not ch: continue
    print('=== %s (%d개)' % (n, len(ch))); total += len(ch)
    for k, a, b in ch:
        print('  %s\n    - %s\n    + %s' % (k, a.replace('\n', '/'), b.replace('\n', '/')))
print('총 %d개 변경' % total)
