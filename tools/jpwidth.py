# 일본판 원문의 줄 폭을 SELT 진행폭에서 직접 재어 창별 실제 한계를 확인한다.
#   python tools/jpwidth.py                 (창 종류별 요약)
#   python tools/jpwidth.py --dump out.json (줄별 폭 전부)
# SELT 글자 코드에는 글자마다 진행폭이 들어 있으므로, 원문이 지킨 폭이 곧 창의 실제 한계다.
# 무전 창은 전각 12자(288px)에서 일관되게 끊기고, 스테이지 종료 대화(0000_3**/4**)와
# 데모·브리핑은 그보다 넓은 창을 쓴다. check_ko.py / build.py 의 한계값 근거.
import sys, json, collections
import paths
from fpctree import parse_file
from gcfs import read_fst
from kolib import selt_sites
from selt3 import read_selt, line_widths
from limits import window_of, LIMITS

TARGETS = [
    ('/movie/m0111.fpc', 'm0111'), ('/movie/m0121.fpc', 'm0121'),
    ('/fpc/s_01_01.fpc', 's01'), ('/fpc/s_02_01.fpc', 's02'), ('/fpc/s_03_01.fpc', 's03'),
    ('/fpc/s_04_01.fpc', 's04'), ('/movie/m0541.fpc', 'm0541'), ('/fpc/s_05_01.fpc', 's05'),
    ('/movie/m0641.fpc', 'm0641'), ('/fpc/s_06_01.fpc', 's06'), ('/fpc/s_07_01.fpc', 's07'),
    ('/fpc/s_08_01.fpc', 's08'), ('/movie/m3100.fpc', 'm3100'), ('/fpc/s_09_01.fpc', 's09'),
    ('/movie/m3200.fpc', 'm3200'), ('/fpc/s_10_01.fpc', 's10'), ('/movie/m1041.fpc', 'm1041'),
    ('/movie/m2300.fpc', 'm2300'),
] + [('/fpc/b0%d01.fpc' % i, 'b0%d' % i) for i in range(1, 10)] + [('/disk.pac', 'disk')]

def scan():
    f, gid, name, dol, ents = read_fst(paths.jp_iso())
    loc = {p: (o, s) for p, o, s in ents}
    out = {}
    for path, js in TARGETS:
        f.seek(loc[path][0]); data = f.read(loc[path][1])
        for bi, (lst, k) in enumerate(selt_sites(parse_file(data))):
            orig = read_selt(lst.items[k].body.data)
            rows = []
            for nm, texts in orig:
                w = texts[0]
                if w and (w[0] >> 16) == 0xA000: w = w[1:]          # 화자 헤더 제외
                rows.append({'name': nm, 'widths': line_widths(w)})
            out['%s#%d' % (js, bi)] = {'n': len(orig), 'rows': rows}
    return out

if __name__ == '__main__':
    out = scan()
    if '--dump' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--dump') + 1], 'w', encoding='utf-8'), ensure_ascii=False)
    g = collections.defaultdict(collections.Counter)
    for k, b in out.items():
        for r in b['rows']:
            g[window_of(k.split('#')[0], r['name'], b['n'])][max(r['widths'])] += 1
    print('%-6s %6s %6s  %s' % ('창', '한계', '원문최대', '원문 폭 상위 분포(폭:줄수)'))
    for win in sorted(g):
        c = g[win]
        print('%-6s %6d %6d  %s' % (win, LIMITS[win], max(c), sorted(c.items())[-5:]))
    over = [(k, r['name'], max(r['widths'])) for k, b in out.items() for r in b['rows']
            if max(r['widths']) > LIMITS[window_of(k.split('#')[0], r['name'], b['n'])]]
    print('한계를 넘는 원문 %d줄%s' % (len(over), (': ' + str(over)) if over else ''))
