import json, sys, glob

NEED_JP = '원문(jp)이 없는 번역 파일입니다. README 의 "번역 수정" 항목대로 ISO 에서 원문을 다시 추출해 쓰세요.'
tm={}
for p in sys.argv[2:]:
    for bl in json.load(open(p,encoding='utf-8')):
        for e in bl['entries']:
            if e['ko']: tm[(e['name'],e['jp'])]=e['ko']
b=json.load(open(sys.argv[1],encoding='utf-8'))
assert 'jp' in b[0]['entries'][0], NEED_JP
for bi,bl in enumerate(b):
    print('== block',bi,bl['first'],len(bl['entries']))
    for e in bl['entries']:
        if (e['name'],e['jp']) in tm: continue
        print(f"{e['name']}[{e['speaker']}] {e['jp']!r} || {e['en']!r}")
