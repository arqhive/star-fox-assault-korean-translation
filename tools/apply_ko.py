import json, sys, importlib.util
js, kopy = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('k', kopy); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
b = json.load(open(js, encoding='utf-8')); miss = []; extra = {f: set(m) for f, m in k.KO.items()}
for bl in b:
    m = k.KO.get(bl['first'], {})
    for e in bl['entries']:
        if e['name'] in m: e['ko'] = m[e['name']]; extra[bl['first']].discard(e['name'])
        else: miss.append((bl['first'], e['name']))
json.dump(b, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('missing', miss, 'unused', {a: v for a, v in extra.items() if v})
