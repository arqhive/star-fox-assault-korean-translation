# translation/ko/*.json 의 번역을 원고(translation/drafts/*_ko.py)에 반영한다.
#   python tools/sync_ko.py            (차이만 보여줌)
#   python tools/sync_ko.py --apply
# 한 줄에 항목 하나인 형태만 다룬다. f-문자열(f'{P}\n…')은 치환 자리가 있어 건드리지 않는다.
import json, glob, re, sys
import paths

LINE = re.compile(r"^(\s*'([\w]+)':\s*(f?)')([^']*)('\s*,?\s*)$")

def main(apply=False):
    ko = {}
    for fn in glob.glob(str(paths.KO / '*.json')):
        b = json.load(open(fn, encoding='utf-8'))
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl.get('entries', []):
                if e.get('ko'): ko[e['name']] = e['ko']
    total = 0
    for fn in sorted(glob.glob(str(paths.DRAFTS / '*_ko.py'))):
        out = []; ch = 0
        for line in open(fn, encoding='utf-8').read().split('\n'):
            m = LINE.match(line)
            if m and m.group(2) in ko:
                fstr, body = m.group(3), m.group(4)
                want = ko[m.group(2)].replace('\\', '\\\\').replace('\n', '\\n')
                if fstr and '{' in body:          # 치환 자리가 있는 원고는 끝 문장부호만 맞춤
                    tail = want[-1] if want and want[-1] in '.!?' else ''
                    if tail and not body.endswith(('.', '!', '?', '…', '~')):
                        line = m.group(1) + body + tail + m.group(5); ch += 1
                elif body != want:
                    if not apply: print('%s %s\n    - %s\n    + %s' % (fn.split('\\')[-1], m.group(2), body, want))
                    line = m.group(1) + want + m.group(5); ch += 1
            out.append(line)
        if ch:
            total += ch
            if apply: open(fn, 'w', encoding='utf-8', newline='').write('\n'.join(out))
            print(fn.split('\\')[-1], ch)
    print('총 %d줄' % total)

if __name__ == '__main__':
    main('--apply' in sys.argv)
