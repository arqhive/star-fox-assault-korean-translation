# 누적 한글 빌드: python build_all.py [출력 ISO]
import json, sys, os, re, struct
from kolib import *

JP_ISO = '../Star Fox - Assault (Japan).iso'
TARGETS = [  # (디스크 경로, 번역 JSON, 무전 복사본 pac)
    ('/movie/m0111.fpc', 'text/m0111.json', None),
    ('/movie/m0121.fpc', 'text/m0121.json', None),
    ('/fpc/s_01_01.fpc', 'text/s01.json', '/attract/comm01.pac'),
    ('/fpc/s_02_01.fpc', 'text/s02.json', '/attract/comm02.pac'),
    ('/fpc/s_03_01.fpc', 'text/s03.json', '/attract/comm03.pac'),
    ('/fpc/s_04_01.fpc', 'text/s04.json', '/attract/comm04.pac'),
    ('/movie/m0541.fpc', 'text/m0541.json', None),
    ('/fpc/s_05_01.fpc', 'text/s05.json', '/attract/comm05.pac'),
    ('/movie/m0641.fpc', 'text/m0641.json', None),
    ('/fpc/s_06_01.fpc', 'text/s06.json', '/attract/comm06.pac'),
    ('/fpc/s_07_01.fpc', 'text/s07.json', '/attract/comm07.pac'),
    ('/fpc/s_08_01.fpc', 'text/s08.json', '/attract/comm08.pac'),
    ('/movie/m3100.fpc', 'text/m3100.json', None),
    ('/fpc/s_09_01.fpc', 'text/s09.json', '/attract/comm09.pac'),
    ('/movie/m3200.fpc', 'text/m3200.json', None),
    ('/fpc/s_10_01.fpc', 'text/s10.json', '/attract/comm10.pac'),
    ('/movie/m1041.fpc', 'text/m1041.json', None),
    ('/movie/m2300.fpc', 'text/m2300.json', None),
] + [('/fpc/b0%d01.fpc' % i, 'text/b0%d.json' % i, None, False) for i in range(1, 10)] + [
    ('/disk.pac', 'text/disk.json', None, False),
]
LIMITS = {'radio': 408, 'demo': 504}

f, gid, name, dol, ents = read_fst(JP_ISO)
loc = {p: (o, s) for p, o, s in ents}
def disk(path):
    o, s = loc[path]; f.seek(o); return f.read(s)

out_files = {}; over = []
for path, js, comm, *opt in TARGETS:
    blocks = json.load(open(js, encoding='utf-8'))
    empty = [(b['first'], e['name']) for b in blocks for e in b['entries'] if not e['ko']]
    assert not empty, empty
    kana = [(e['name'], e['ko']) for b in blocks for e in b['entries']
            if re.search(r'[぀-ヿ一-鿿]', TOKEN.sub('', e['ko']))]
    assert not kana, kana
    data, res = localize_file(disk(path), blocks, over, LIMITS, center=opt[0] if opt else None)
    out_files[path] = data
    print(path, 'blocks', len(blocks), 'max glyphs', max(len(a.glyphs) for _, _, a in res.values()))
    if comm:
        radio = [bi for bi in res if len(blocks[bi]['entries']) > 100]
        assert len(radio) == 1
        c = parse_file(disk(comm))
        assert c.items[1].body.data[:4] == b'SELT'
        c.items[0].body = res[radio[0]][0].body; c.items[1].body = res[radio[0]][1].body
        out_files[comm] = c.ser()
for o in over: print('  폭 초과:', o)
if over: sys.exit('폭 초과 줄을 수정하세요')
# 메뉴(ROM 폰트) 한글화
import build_menu
f.seek(0x420); dol_off = struct.unpack('>I', f.read(4))[0]
f.seek(dol_off); _h = f.read(0x100)
_end = max(struct.unpack('>I', _h[i*4:i*4+4])[0] + struct.unpack('>I', _h[0x90+i*4:0x94+i*4])[0] for i in range(18))
f.seek(dol_off); dol_bytes = f.read(_end)
menu_files, new_dol, komap = build_menu.build(disk, dol_bytes)
out_files.update(menu_files)
print('menu files', len(menu_files))
import build_tex
out_files.update(build_tex.build(disk, out_files))
if len(sys.argv) > 1:
    rebuild_iso(JP_ISO, sys.argv[1], out_files, new_dol=new_dol)
    verify_iso(JP_ISO, sys.argv[1], out_files, new_dol=new_dol)
