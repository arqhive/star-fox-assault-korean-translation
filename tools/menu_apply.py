import json, importlib.util, re
spec = importlib.util.spec_from_file_location('m', 'text/menu_ko.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
missing = []
for f in ['select', 'resvs', 'ressc1', 'ressc2']:
    b = json.load(open(f'text/{f}.json', encoding='utf-8'))
    for e in b[0]['entries']:
        if e['jp'].startswith('{5345:'): e['ko'] = e['jp']; continue
        k = m.ko_for(e['name'], e['jp'])
        if k is None: missing.append((f, e['name'], e['jp']))
        else: e['ko'] = k
    json.dump(b, open(f'text/{f}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('missing', missing)
