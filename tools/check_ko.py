# 번역 검사: 빈 줄·한자/가나 혼입·줄 폭 초과·줄 수
#   python tools/check_ko.py               (전체)
#   python tools/check_ko.py s01 b03       (일부 — translation/ko 의 파일 이름)
import json, re, sys
import paths
from kolib import split_units, ink, is_hangul, SPACE_ADV, HANGUL_ADV, CELL

LIMIT_RADIO, LIMIT_DEMO = 408, 504      # 무전 창 / 데모·무비 자막 최대 폭(px)
MAX_LINES = 3
KANA = re.compile(r'[぀-ヿ一-鿿]')
TOKEN = re.compile(r'\{([0-9a-fA-F]{4}):(\d+)\}')

def adv(ch):
    if ch == ' ': return SPACE_ADV
    if is_hangul(ch): return HANGUL_ADV
    l, r = ink(ch)
    return min(CELL, (r - l) + 3)

def line_widths(text):
    out = [0]
    for u in split_units(text):
        if u[0] == 'nl': out.append(0)
        elif u[0] == 'ch': out[-1] += adv(u[1])
    return out

MENU = {'select', 'resvs', 'ressc1', 'ressc2'}      # 메뉴는 본체 ROM 폰트라 폭·줄 수 제한이 다름

def check(name):
    path = paths.KO / (name + '.json')
    blocks = json.load(open(path, encoding='utf-8'))
    if isinstance(blocks, dict): blocks = [blocks]
    bad = []
    for bl in blocks:
        limit = LIMIT_RADIO if len(bl['entries']) > 100 else LIMIT_DEMO
        for e in bl['entries']:
            ko = e.get('ko') or ''
            if not ko.strip():
                bad.append((e['name'], '빈 줄')); continue
            if KANA.search(TOKEN.sub('', ko).replace('・', '')):   # ・(가운뎃점)은 원문 그대로 씀
                bad.append((e['name'], '한자·가나 혼입: %s' % ko.replace('\n', '/')))
            if name in MENU: continue
            w = line_widths(ko)
            if max(w) > limit:
                bad.append((e['name'], '폭 초과 %dpx > %d: %s' % (max(w), limit, ko.replace('\n', '/'))))
            if len(w) > MAX_LINES:
                bad.append((e['name'], '%d줄: %s' % (len(w), ko.replace('\n', '/'))))
    return bad

if __name__ == '__main__':
    names = sys.argv[1:] or sorted(p.stem for p in paths.KO.glob('*.json'))
    total = 0
    for n in names:
        bad = check(n)
        total += len(bad)
        for nm, msg in bad: print('%-8s %-14s %s' % (n, nm, msg))
    print('문제 %d개' % total)
    sys.exit(1 if total else 0)
