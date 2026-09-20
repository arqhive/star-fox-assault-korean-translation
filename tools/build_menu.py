# 메뉴(ROM 폰트) 한글화: 한글 SJIS 폰트 + DOL 패치 + 메뉴 SELT 4종 + rel 문자열
import json
from kofont import *
from fpctree import *
from kolib import selt_sites
import paths

MENU_FILES = {'/fpc/select.fpc': 'select.json', '/fpc/resvs.fpc': 'resvs.json',
              '/fpc/ressc1.fpc': 'ressc1.json', '/fpc/ressc2.fpc': 'ressc2.json'}
REL_STRINGS = {  # (파일, 오프셋, 원문, 번역) — 번역 바이트 수는 원문 이하
 '/m2.rel': [(0x181f8, 'しない', '끔'), (0x18200, 'する', '켬'), (0x184ec, 'ポイント', '포인트'), (0x184f8, 'タイム', '타임'),
             (0x18500, 'サバイバル', '서바이벌'), (0x1850c, 'なし', '없음'), (0x18514, 'あり', '있음'),
             (0x185e8, 'アーウィン', '아윙'), (0x18600, 'ランドマスター', '랜드마스터'), (0x1861c, 'パイロット', '파일럿'),
             (0x18654, 'ユーザーセッティング', '사용자 설정'), (0x187f8, 'レベルセレクト', '레벨 선택'),
             (0x18a2c, 'オプション', '옵션'), (0x18a44, 'ユーザーセッティング', '사용자 설정'), (0x18a6c, 'プレイデータ', '플레이 데이터'),
             (0x18a88, 'サウンド', '사운드'), (0x18c60, '倒した回数', '격파 횟수'), (0x18c80, '倒された回数', '쓰러진 횟수'),
             (0x18cf0, 'バトルスコア', '배틀 스코어'),
             (0x186b4, '小', '소'), (0x186bc, '大', '대')],   # 배틀 핸디캡 설정값
 '/m3.rel': [(0x9bac, 'リザルト', '결과'), (0x9bf0, '倒した数', '격파 수'), (0x9c14, '倒された数', '쓰러진 수'),
             (0x9d14, 'リザルト', '결과')],
}

# 이름 입력 글자표 (m2.rel, 5줄×12칸, 줄 우선): 히라가나표 → 한글 기본음절, 가타카나표 → 등장인물 이름 음절 등
_C1 = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌ'
def _syl(c, v): return chr(0xAC00 + ('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'.index(c) * 21 + 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'.index(v)) * 28)
NAME_TABLE1 = ''.join(_syl(c, v) for v in 'ㅏㅓㅗㅜㅣ' for c in _C1).replace('치', '')   # 마지막 줄은 11칸
NAME_TABLE2 = ('파퍼포푸피하허호후히에애'
               '스크트그프드르므브츠즈흐'
               '레페제네데세베케테메헤게'
               '폭팔탈슬울팬온벨임앤윙넬'
               '민준영진현성은윤석철김')
NAME_TABLES = [(0x18040, 'あかさた', NAME_TABLE1), (0x180B8, 'アカサタ', NAME_TABLE2)]
assert len(NAME_TABLE1) == len(set(NAME_TABLE1)) == 59 and len(NAME_TABLE2) == len(set(NAME_TABLE2)) == 59 and not set(NAME_TABLE1) & set(NAME_TABLE2)

# 배틀 핸디캡 설정값: 원래 자리(小/大)는 4바이트뿐이라 '작게/크게'가 안 들어간다.
# '유저 세팅'으로 짧아진 0x18654 문자열 뒤 빈칸에 새 문자열을 넣고,
# 그 자리를 가리키던 재배치(relocation) addend 를 새 위치로 돌린다.
REL_MOVED = {'/m2.rel': (4, [(0x704, '작게'), (0x70c, '크게')])}   # (데이터 섹션 번호, [원래 addend, 번역])

def room_at(buf, off, src, cap=64):
    """원문 뒤 정렬 패딩(0 바이트)까지 포함해 쓸 수 있는 칸 수. 널 종료 자리를 포함한다"""
    n = len(src)
    while n < cap and off + n < len(buf) and buf[off + n] == 0: n += 1
    return n

def move_rel_strings(d, sec_no, items, komap, gaps):
    """문자열을 빈칸으로 옮기고 그것을 가리키는 재배치 항목의 addend 를 고친다"""
    nsec, secoff = struct.unpack('>II', d[0x0c:0x14])
    impoff, impsz = struct.unpack('>II', d[0x28:0x30])
    base = struct.unpack('>I', d[secoff + sec_no * 8:secoff + sec_no * 8 + 4])[0] & ~3
    remap = {}
    gaps = sorted(gaps, key=lambda g: -g[1])
    for oldadd, ko in items:
        kb = sjis_bytes(ko, komap) + bytes(1)
        for i, (start, size) in enumerate(gaps):
            if size >= len(kb) and start >= base:
                assert not any(d[start:start + len(kb)]), ('빈칸이 아님', hex(start))
                d[start:start + len(kb)] = kb
                remap[oldadd] = start - base
                gaps[i] = (start + len(kb), size - len(kb))
                break
        else:
            raise AssertionError('옮길 빈칸이 부족하다: ' + ko)
    n = 0
    for k in range(impsz // 8):
        p = struct.unpack('>I', d[impoff + k * 8 + 4:impoff + k * 8 + 8])[0]
        while True:
            off, typ, rs, add = struct.unpack('>HBBI', d[p:p + 8])
            if typ == 203: break
            if typ not in (201, 202) and rs == sec_no and add in remap:
                struct.pack_into('>I', d, p + 4, remap[add]); n += 1
            p += 8
    assert n == 2 * len(items), ('재배치 항목 수가 예상과 다름', n)

# DOL 안 부팅 시스템 메시지: 한 글자가 32비트 C000xxxx(xxxx=SJIS, ASCII 는 <<8), 끝은 00000000.
# 본체 ROM 폰트로 그리므로 한글을 한자 칸에 넣은 우리 폰트에서는 일부 글자가 한글로 깨져 보인다.
# (오프셋은 DOL 파일 기준. 번역은 원문 글자 수 이하)
DOL_WIDE = [
    (0x230210, 'ディスクカバーが開いています。ゲームを', '디스크 커버가 열려 있습니다. '),
    (0x230264, '続ける', '게임을'),
    (0x230274, '場合はディスクカバーを', ' 계속하려면 커버를'),
    (0x2302a4, '閉めてください。', ' 닫아 주세요.'),
    (0x23042c, 'スターフォックス アサルトのディスクを', '스타폭스 어설트 디스크를 '),
    (0x23047c, 'セットしてください。', '넣어 주세요.'),
    (0x230560, 'ディスクを読めませんでした。くわしくは', '디스크를 읽지 못했습니다. '),
    (0x2305b0, '本体の', '본체의'),
    (0x2305ec, '取扱説明書をお読みください。', ' 설명서를 읽어 주세요.'),
    (0x230798, 'プログレッシブモードで表示しますか？', '프로그레시브 모드로 표시할까요?'),
    (0x2308b4, 'はい', '예'),
    (0x2308d0, 'いいえ', '아니요'),
    (0x2308ec, '画面表示モードはプログレッシブモードに', '화면 모드가 프로그레시브 모드로 '),
    (0x23093c, 'セットされました。　Ａボタンを押して下さい。', '설정되었습니다. A 버튼을 누르세요.'),
    (0x230a90, '画面表示モードはインターレースモードに', '화면 모드가 인터레이스 모드로 '),
    (0x230ae0, 'セットされました。', '설정되었습니다.'),
]

def wide_char(ch, komap):
    if ch in komap.map: return 0xC0000000 | komap.map[ch]
    b = ch.encode('shift_jis')
    return 0xC0000000 | ((b[0] << 8 | b[1]) if len(b) == 2 else (b[0] << 8))

def patch_dol_wide(db, komap):
    """C000 형식 문자열 교체: 원문 확인 → 한글로 다시 쓰고 00000000 으로 끝낸다"""
    for off, jp, ko in DOL_WIDE:
        n = 0
        while struct.unpack('>I', db[off + n*4:off + n*4 + 4])[0] >> 16 == 0xC000: n += 1
        got = ''
        for k in range(n):
            c = struct.unpack('>I', db[off + k*4:off + k*4 + 4])[0] & 0xFFFF
            hi, lo = c >> 8, c & 0xFF
            got += chr(hi) if lo == 0 and hi < 0x80 else bytes([hi, lo]).decode('shift_jis')
        assert got == jp, (hex(off), got, jp)
        assert len(ko) <= n, (hex(off), len(ko), n, ko)
        out = b''.join(struct.pack('>I', wide_char(c, komap)) for c in ko) + bytes(4)
        db[off:off + len(out)] = out

DOL_STRINGS = [(0x21D8A0, '新規登録', '신규 등록'), (0x21DA54, 'ゲスト', '게스트'),
               (0x29CDCC, 'はい', '예'), (0x29CDDC, 'いいえ', '아니요')]   # DOL 파일 오프셋

def sjis_bytes(text, komap):
    out = b''
    for ch in text:
        if ch in komap.map: out += bytes([komap.map[ch] >> 8, komap.map[ch] & 0xFF])
        else: out += ch.encode('shift_jis')
    return out

def build(disk, dol_bytes):
    menus = {p: json.load(open(paths.KO / js, encoding='utf-8')) for p, js in MENU_FILES.items()}
    texts = ([NAME_TABLE1, NAME_TABLE2] + [e['ko'] for b in menus.values() for e in b[0]['entries']]
             + [k for v in REL_STRINGS.values() for _, _, k in v] + [k for _, _, k in DOL_STRINGS]
             + [k for _, _, k in DOL_WIDE] + [k for _, items in REL_MOVED.values() for _, k in items])
    komap = KoMap(texts)
    raw, comp = build_font(komap, paths.WORK / 'ko_font.szp')
    db = bytearray(dol_bytes)
    for off, jp, ko in DOL_STRINGS:
        src = jp.encode('shift_jis'); assert db[off:off+len(src)] == src and db[off+len(src)] == 0, (hex(off), jp)
        room = min(room_at(db, off, src), 12)      # 같은 배열의 'New User'(9바이트)를 보면 이름 칸은 12바이트 이상
        kb = sjis_bytes(ko, komap); assert len(kb) < room, (ko, len(kb), room)
        db[off:off+room] = kb.ljust(room, bytes(1))
    patch_dol_wide(db, komap)          # 부팅 시스템 메시지(C000 형식)
    new_dol, arena = patch_dol(bytes(db), comp)
    print('  font: %d hangul, yay0 %d bytes, arena lo -> %08x' % (len(komap), len(comp), arena))
    files = {}
    for p, blocks in menus.items():
        tree = parse_file(disk(p)); (lst, k), = selt_sites(tree)
        orig = read_selt_raw(lst.items[k].body.data)
        ents = []
        for (nm, texts_), e in zip(orig, blocks[0]['entries']):
            assert nm == e['name']
            w0 = texts_[0]
            if w0 is not None and not e['ko'].startswith('{5345:'):
                w0 = encode_menu(e['ko'], komap)
            ents.append((nm, [w0] + texts_[1:]))
        lst.items[k].body = Leaf(build_selt_raw(ents))
        files[p] = tree.ser()
    gaps = {}
    for p, lst in REL_STRINGS.items():
        d = bytearray(disk(p)); gaps[p] = []
        for off, jp, ko in lst:
            src = jp.encode('shift_jis'); assert d[off:off+len(src)] == src and d[off+len(src)] == 0, (p, hex(off))
            room = room_at(d, off, src)
            kb = sjis_bytes(ko, komap); assert len(kb) < room, (ko, len(kb), room)
            d[off:off+room] = kb.ljust(room, bytes(1))
            if room - len(kb) - 1 > 0: gaps[p].append((off + len(kb) + 1, room - len(kb) - 1))
        files[p] = bytes(d)
    d = bytearray(files['/m2.rel'])
    for pth, (sec_no, items) in REL_MOVED.items():
        dd = bytearray(files[pth]) if pth != '/m2.rel' else d
        move_rel_strings(dd, sec_no, items, komap, gaps.get(pth, []))
        if pth != '/m2.rel': files[pth] = bytes(dd)
    for off, head, table in NAME_TABLES:
        assert d[off:off + 8] == head.encode('shift_jis'), hex(off)
        n = 0
        while d[off + 2 * n:off + 2 * n + 2] != b'\0\0': n += 1
        assert n == 59, (hex(off), n)
        d[off:off + 118] = sjis_bytes(table, komap)
    files['/m2.rel'] = bytes(d)
    return files, new_dol, komap
