# 스타폭스 어썰트 한글 빌드 공용 라이브러리
import re, struct, os, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fpctree import *
from selt3 import read_selt
from gcfs import read_fst

CELL, COLS, TEXW = 24, 42, 1024
FONT = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 20)
SPACE_ADV = 8
_dr = ImageDraw.Draw(Image.new('L', (1, 1)))
TOKEN = re.compile(r'\{([0-9a-fA-F]{4}):(\d+)\}')

def is_hangul(ch): return '\uac00' <= ch <= '\ud7a3'
def ink(ch):
    l, t, r, b = _dr.textbbox((0, 0), ch, font=FONT); return l, r
HANGUL_ADV = 22

def split_units(text):
    """문자열 → 단위 목록: ('ch', c) / ('nl',) / ('code', 32bit)"""
    out = []; p = 0
    for m in TOKEN.finditer(text):
        out += [('nl',) if c == '\n' else ('ch', c) for c in text[p:m.start()]]
        out.append(('code', (int(m.group(1), 16) << 16) | int(m.group(2))))
        p = m.end()
    out += [('nl',) if c == '\n' else ('ch', c) for c in text[p:]]
    return out

class Atlas:
    def __init__(self):
        self.glyphs = []; self.idx = {}
    def add_text(self, text):
        for u in split_units(text):
            if u[0] == 'ch' and u[1] != ' ' and u[1] not in self.idx:
                self.glyphs.append(u[1]); self.idx[u[1]] = len(self.glyphs)
    def finalize(self):
        self.space = len(self.glyphs) + 1
        self.adv = {' ': SPACE_ADV}
        n = len(self.glyphs) + 1
        rows = (n + COLS - 1) // COLS
        tex = np.zeros((rows*CELL, TEXW), np.uint8)
        for i, ch in enumerate(self.glyphs):
            l, r = ink(ch); w = r - l
            a = HANGUL_ADV if is_hangul(ch) else min(CELL, w + 3)
            self.adv[ch] = a
            im = Image.new('L', (CELL, CELL), 0); dr = ImageDraw.Draw(im)
            dr.text(((a - w)//2 - l, (CELL - 20)//2 - 5), ch, font=FONT, fill=255)   # 일본판 글리프(2~20행)와 같은 높이
            gy, gx = divmod(i, COLS)
            tex[gy*CELL:(gy+1)*CELL, gx*CELL:(gx+1)*CELL] = np.array(im)
        self.image = tex
        q = (tex.astype(np.int32) * 15 + 127) // 255
        blk = q.reshape(tex.shape[0]//8, 8, TEXW//8, 8).transpose(0, 2, 1, 3).reshape(-1)
        data = ((blk[0::2] << 4) | blk[1::2]).astype(np.uint8).tobytes()
        self.texdata = data + b'\0' * (-len(data) % 0x1000)
        return self

def code_width(v): return (v >> 16) & 0xFF

def encode(text, atlas, header, center):
    """header: 원본 앞부분 코드(화자 A000 + 줄바꿈). center: 무비식 첫 줄 기준 가운데 정렬"""
    lines = [[]]
    for u in split_units(text):
        if u[0] == 'nl': lines.append([]); continue
        if u[0] == 'code': lines[-1].append(u[1]); continue
        c = u[1]
        gi = atlas.space if c == ' ' else atlas.idx[c]
        lines[-1].append(0x20000000 | (atlas.adv[c] << 16) | gi)
    widths = [sum(code_width(v) for v in L) for L in lines]
    words = list(header)
    W = max(widths)
    def blank(px):
        out = []
        while px > 0:
            p = min(px, 0xFF); out.append(0x20000000 | (p << 16) | atlas.space); px -= p
        return out
    for li, L in enumerate(lines):
        if li: words.append(0xFFFFFFFF)
        if center:
            lead = (W - widths[li]) // 2
            words += blank(lead)
        words += L
        if center and li == 0: words += blank(W - widths[0] - lead)
    return words, widths

def build_selt(entries_words):
    """entries_words: [(name, [lang0 words], [lang1 words])]"""
    n = len(entries_words); base = 0x10 + n*0x18
    table = b''; body = b''; off = base
    for nm, w0, w1 in entries_words:
        b0 = b''.join(struct.pack('>I', v) for v in w0 + [0])
        b1 = b''.join(struct.pack('>I', v) for v in w1 + [0])
        table += nm.encode().ljust(16, b'\0') + struct.pack('>II', off, off + len(b0))
        body += b0 + b1; off += len(b0) + len(b1)
    return b'SELT' + struct.pack('>III', n, 2, 0) + table + body

def selt_sites(tree):
    """(부모 NpacList, SELT 항목 번호) 목록을 문서 순서로"""
    out = []
    def rec(node):
        if isinstance(node, NpacList):
            for k, it in enumerate(node.items):
                if it.empty: continue
                if isinstance(it.body, Leaf) and it.body.data[:4] == b'SELT': out.append((node, k))
                else: rec(it.body)
        elif isinstance(node, Container):
            for it in node.items: rec(it)
    rec(tree)
    return out

def localize_file(jp_bytes, blocks, report=None, limits=None, center=None):
    # center: None=화자 헤더 없으면 가운데 정렬(무비), False=정렬 안 함
    """blocks: extract_text JSON 블록 목록(문서 순서). 반환: 새 파일 바이트, 블록별 (tex, selt) Npac"""
    tree = parse_file(jp_bytes)
    sites = selt_sites(tree)
    assert len(sites) == len(blocks), (len(sites), len(blocks))
    # 텍스처 공유 그룹: 텍스처 자리가 FFFFFFFF 자리표시자면 앞 블록과 공유
    def is_selt(it): return not it.empty and isinstance(it.body, Leaf) and it.body.data[:4] == b'SELT'
    tex_of = []
    for lst, k in sites:        # 텍스처 = 앞쪽에서 SELT가 아닌 첫 항목 (브리핑은 텍스처 1개를 SELT 2개가 공유)
        j = k - 1
        while j >= 0 and is_selt(lst.items[j]): j -= 1
        tex_of.append((lst, j))
    groups = []
    for bi, (lst, k) in enumerate(sites):
        tl, tj = tex_of[bi]; tex_item = tl.items[tj]
        shared = tex_item.empty and tex_item.body and tex_item.body[0] == 0xFFFFFFFF
        same = bi > 0 and tex_of[bi - 1][0] is tl and tex_of[bi - 1][1] == tj
        if shared or same: groups[-1].append(bi)
        else: groups.append([bi])
    results = {}
    for g in groups:
        atlas = Atlas()
        for bi in g:
            for e in blocks[bi]['entries']: atlas.add_text(e['ko'])
        atlas.finalize()
        for bi in g:
            lst, k = sites[bi]
            orig = read_selt(lst.items[k].body.data)
            assert [n[:8] for n, _ in orig] == [e['name'][:8] for e in blocks[bi]['entries']]
            ew = []
            for (nm, texts), e in zip(orig, blocks[bi]['entries']):
                w = texts[0]; header = []
                if w and (w[0] >> 16) == 0xA000:
                    header = [w[0]] + ([0xFFFFFFFF] if len(w) > 1 and w[1] == 0xFFFFFFFF else [])
                words, widths = encode(e['ko'], atlas, header, center=(not header) if center is None else center)
                lim = (limits or {}).get('radio' if len(blocks[bi]['entries']) > 100 else 'demo')
                if report is not None and lim and max(widths) > lim:
                    report.append((blocks[bi]['first'], nm, max(widths), e['ko']))
                ew.append((nm, words, texts[1]))
            lst.items[k].body = Leaf(build_selt(ew))
            tl, tj = tex_of[bi]
            if bi == g[0]:
                assert not is_selt(tl.items[tj])
                tl.items[tj].body = Leaf(atlas.texdata)
            results[bi] = (tl.items[tj], lst.items[k], atlas)
    return tree.ser(), results

FREE_START, FREE_END = 0x2C8000, 0x627E314   # FST 뒤 미참조 패딩 영역

def rebuild_iso(src, out, files, align=4, new_dol=None):
    """ISO 전체 재배치: 원래 파일 순서대로 빈틈 없이 다시 채운다.
    크기가 늘어난 만큼 시작 위치를 앞(FST 뒤 미사용 영역)으로 당겨 디스크 크기를 유지."""
    f, gid, name, dol, ents = read_fst(src)
    disc_size = os.path.getsize(src)
    f.seek(0x424); fst_off, fst_size = struct.unpack('>II', f.read(8))
    f.seek(fst_off); fst = bytearray(f.read(fst_size))
    n = struct.unpack('>I', fst[8:12])[0]
    idx = {}
    for i in range(n):
        if fst[i*12] == 0:
            idx[struct.unpack('>II', fst[i*12+4:i*12+12])] = i
    order = sorted(ents, key=lambda e: e[1])
    sizes = [len(files[p]) if p in files else s for p, o, s in order]
    al = lambda v: (v + align - 1) & ~(align - 1)
    total = 0
    for s in sizes: total = al(total) + s
    first = order[0][1]
    start = min(first, (disc_size - total) & ~(align - 1))
    lowest = FREE_START + (len(new_dol) + 0x7FFF & ~0x7FFF if new_dol else 0)
    assert start >= lowest, 'disc overflow: %d bytes' % (lowest - start)
    with open(out, 'wb') as g:
        f.seek(0); g.write(f.read(start))            # 시스템 영역 + FST(나중에 덮어씀) + 앞쪽 패딩
        cur = start
        for (p, o, s), ns in zip(order, sizes):
            pad_to = al(cur)
            if pad_to > cur: g.write(b'\0' * (pad_to - cur)); cur = pad_to
            if p in files:
                g.write(files[p])
            else:
                f.seek(o); left = s
                while left:
                    chunk = f.read(min(left, 1 << 24)); g.write(chunk); left -= len(chunk)
            e = idx[(o, s)]
            fst[e*12+4:e*12+12] = struct.pack('>II', cur, ns)
            cur += ns
        assert cur <= disc_size
        g.write(b'\0' * (disc_size - cur))
        g.seek(fst_off); g.write(fst)
        if new_dol:   # DOL을 FST 뒤 빈 영역으로 옮기고 헤더 0x420 갱신
            g.seek(FREE_START); g.write(new_dol)
            g.seek(0x420); g.write(struct.pack('>I', FREE_START))
    print('  rebuilt: start %08x (orig %08x), end %08x / %08x' % (start, first, cur, disc_size))

def verify_iso(src, out, files, new_dol=None):
    """변경 파일은 새 내용과, 나머지는 원본과 바이트 비교"""
    import hashlib
    f1, *_, e1 = read_fst(src); f2, *_, e2 = read_fst(out)
    l2 = {p: (o, s) for p, o, s in e2}
    assert set(l2) == {p for p, _, _ in e1}
    for p, o, s in e1:
        o2, s2 = l2[p]; f2.seek(o2); d2 = f2.read(s2)
        if p in files: assert d2 == files[p], p
        else:
            f1.seek(o); assert f1.read(s) == d2, p
    # 부트 헤더·dol·apploader 영역 동일
    f1.seek(0); f2.seek(0); h1 = bytearray(f1.read(0x2440)); h2 = bytearray(f2.read(0x2440))
    if new_dol:
        assert struct.unpack('>I', h2[0x420:0x424])[0] == FREE_START
        f2.seek(FREE_START); assert f2.read(len(new_dol)) == new_dol, 'dol'
        h1[0x420:0x424] = h2[0x420:0x424]
    assert h1 == h2
    print('  verify OK: %d files (%d changed)' % (len(e1), len(files)))

def patch_iso(src, out, files):
    """files: {디스크 경로: 새 바이트}. 원래 자리에 들어가면 제자리, 아니면 빈 영역에 배치"""
    if not os.path.exists(out) or os.path.getsize(out) != os.path.getsize(src):
        shutil.copyfile(src, out)
    f, gid, name, dol, ents = read_fst(src)
    f.seek(0x424); fst_off = struct.unpack('>I', f.read(4))[0]
    f.seek(fst_off); hdr = f.read(12); n = struct.unpack('>I', hdr[8:12])[0]
    f.seek(fst_off); fst = f.read(n*12)
    loc = {p: (o, s) for p, o, s in ents}
    cursor = FREE_START
    with open(out, 'r+b') as g:
        for path, data in files.items():
            o, s = loc[path]
            ent = next(i for i in range(n) if fst[i*12] == 0 and struct.unpack('>II', fst[i*12+4:i*12+12]) == (o, s))
            if len(data) <= s:
                new_off = o
            else:
                new_off = cursor; cursor = (cursor + len(data) + 0x7FFF) & ~0x7FFF
                assert cursor <= FREE_END, 'free area overflow'
            g.seek(new_off); g.write(data)
            g.seek(fst_off + ent*12 + 4); g.write(struct.pack('>II', new_off, len(data)))
            print('  %-24s %8d -> %8d @ %08x' % (path, s, len(data), new_off))
