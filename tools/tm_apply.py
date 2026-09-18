# 번역 메모리 + 파일 번역 적용: python tm_apply.py text/s02.json text/s02_ko.py [이전 json...]
import json, sys, importlib.util

NEED_JP = '원문(jp)이 없는 번역 파일입니다. README 의 "번역 수정" 항목대로 ISO 에서 원문을 다시 추출해 쓰세요.'
js, kopy, prev = sys.argv[1], sys.argv[2], sys.argv[3:]
spec = importlib.util.spec_from_file_location('k', kopy); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
tm = {}
for p in prev:
    for bl in json.load(open(p, encoding='utf-8')):
        for e in bl['entries']:
            if e['ko']: tm[(e['name'], e['jp'])] = e['ko']
b = json.load(open(js, encoding='utf-8')); miss = []; used = set(); n_tm = 0
assert 'jp' in b[0]['entries'][0], NEED_JP
for bl in b:
    m = k.KO.get(bl['first'], {})
    for e in bl['entries']:
        if e['name'] in m: e['ko'] = m[e['name']]; used.add((bl['first'], e['name']))
        elif (e['name'], e['jp']) in tm: e['ko'] = tm[(e['name'], e['jp'])]; n_tm += 1
        else: miss.append((bl['first'], e['name'], e['jp']))
unused = [(f, n) for f, m in k.KO.items() for n in m if (f, n) not in used]
json.dump(b, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(js, 'TM', n_tm, 'missing', miss, 'unused', unused)
