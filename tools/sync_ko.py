# text/*.json 의 ko 를 번역 원고(*_ko.py)에 반영: 항목 이름이 같은 줄의 문자열 끝 문장부호를 맞춤
import json, glob, re, sys
ko = {}
for fn in glob.glob('text/*.json'):
    b = json.load(open(fn, encoding='utf-8'))
    for bl in (b if isinstance(b, list) else [b]):
        for e in bl.get('entries', []):
            if e.get('ko'): ko[e['name']] = e['ko']
LINE = re.compile(r"^(\s*'([\w]+)':\s*f?')([^']*)('\s*,?\s*)$")   # 한 줄에 항목 하나인 경우만
n = 0
for fn in sorted(glob.glob('text/*_ko.py')):
    out = []; ch = 0
    for line in open(fn, encoding='utf-8').read().split('\n'):
        m = LINE.match(line)
        if m and m.group(2) in ko:
            body = m.group(3); want = ko[m.group(2)]
            tail = want[-1] if want and want[-1] in '.!?,' else ''
            if tail and not body.endswith(('.', '!', '?', '…', '~')):
                line = m.group(1) + body + tail + m.group(4); ch += 1
            elif ', ' in want and body.replace(', ', ' ') == want.replace(', ', ' ').replace('\n', '\n') and body != want.replace('\n', '\n'):
                line = m.group(1) + want.replace('\n', '\n') + m.group(4); ch += 1
        out.append(line)
    if ch:
        open(fn, 'w', encoding='utf-8').write('\n'.join(out)); n += ch; print(fn, ch)
print('총', n)
