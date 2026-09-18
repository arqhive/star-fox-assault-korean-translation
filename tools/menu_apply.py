import json, importlib.util, re

NEED_JP = '원문(jp)이 없는 번역 파일입니다. README 의 "번역 수정" 항목대로 ISO 에서 원문을 다시 추출해 쓰세요.'
import paths
spec = importlib.util.spec_from_file_location('m', str(paths.DRAFTS / 'menu_ko.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
missing = []
for f in ['select', 'resvs', 'ressc1', 'ressc2']:
    b = json.load(open(paths.KO / f'{f}.json', encoding='utf-8'))
    assert 'jp' in b[0]['entries'][0], NEED_JP
    for e in b[0]['entries']:
        if e['jp'].startswith('{5345:'): e['ko'] = e['jp']; continue
        k = m.ko_for(e['name'], e['jp'])
        if k is None: missing.append((f, e['name'], e['jp']))
        else: e['ko'] = k
    json.dump(b, open(paths.KO / f'{f}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('missing', missing)
