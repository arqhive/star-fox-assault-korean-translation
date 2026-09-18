import json, sys, glob
tm={}
for p in sys.argv[2:]:
    for bl in json.load(open(p,encoding='utf-8')):
        for e in bl['entries']:
            if e['ko']: tm[(e['name'],e['jp'])]=e['ko']
b=json.load(open(sys.argv[1],encoding='utf-8'))
for bi,bl in enumerate(b):
    print('== block',bi,bl['first'],len(bl['entries']))
    for e in bl['entries']:
        if (e['name'],e['jp']) in tm: continue
        print(f"{e['name']}[{e['speaker']}] {e['jp']!r} || {e['en']!r}")
