# 여러 파일에 복사돼 있는 같은 이름의 대사를 한 벌로 맞춘다.
# 기준(owner): 이름 앞 4자리의 미션 번호에 해당하는 파일 (0000_ 공용 무전은 s01)
#   python tools/sync_dup.py            (차이만 보여줌)
#   python tools/sync_dup.py --apply
import json, sys
import paths

def load(p):
    b = json.load(open(p, encoding='utf-8'))
    return b if isinstance(b, list) else [b]

def owner_of(name):
    if name[:4].isdigit():
        n = int(name[:2])
        return 's%02d' % (n if 1 <= n <= 10 else 1)
    return None

def main(apply=False):
    files = {p.stem: p for p in sorted(paths.KO.glob('*.json'))}
    data = {k: load(v) for k, v in files.items()}
    where = {}
    for k, blocks in data.items():
        for bl in blocks:
            for e in bl['entries']: where.setdefault(e['name'], {})[k] = e['ko']
    diffs = 0; fixed = set()
    for name, vals in where.items():
        if len(set(vals.values())) == 1: continue
        own = owner_of(name)
        if own not in vals: own = sorted(vals)[0]
        good = vals[own]
        diffs += 1
        print('%s  (기준 %s)' % (name, own))
        for k, v in sorted(vals.items()):
            if v != good: print('   %-7s %s' % (k, v.replace('\n', '/')))
        print('   %-7s %s  ←' % (own, good.replace('\n', '/')))
        if apply:
            for k, blocks in data.items():
                for bl in blocks:
                    for e in bl['entries']:
                        if e['name'] == name and e['ko'] != good: e['ko'] = good; fixed.add(k)
    if apply and fixed:
        for k in fixed:
            json.dump(data[k], open(files[k], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('맞춘 파일:', ', '.join(sorted(fixed)))
    print('다른 항목 %d개' % diffs)

if __name__ == '__main__':
    main('--apply' in sys.argv)
