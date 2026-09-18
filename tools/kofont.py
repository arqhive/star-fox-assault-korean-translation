# 메뉴용 한글 SJIS 폰트(ROM 폰트 대체) 생성 + DOL 패치 + 메뉴 SELT 인코딩
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from yay0 import decompress, compress
from gcfont import Font, sjis_index
from dol import Dol

import os
BASE_FONT = os.environ.get('GC_FONT_JAPANESE', '../../Dolphin-x64/Sys/GC/font_japanese.bin')   # Dolphin Sys/GC/font_japanese.bin
KO_FONT = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 19)
KANJI_START = 0x889F

def kanji_codes():
    """JIS 1수준 한자 SJIS 코드를 순서대로 (0x889F~0x9872)"""
    for hi in range(0x88, 0x99):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            c = (hi << 8) | lo
            if KANJI_START <= c <= 0x9872: yield c

class KoMap:
    """한글 음절 → SJIS 한자 코드 배정 (전역, 메뉴 파일 공통)"""
    def __init__(self, texts):
        chars = []
        for t in texts:
            for ch in t:
                if '\uac00' <= ch <= '\ud7a3' and ch not in chars: chars.append(ch)
        codes = kanji_codes()
        self.map = {ch: next(codes) for ch in chars}
    def __len__(self): return len(self.map)

def render_glyph(ch, cell=24, top=3, bottom=19):
    """원래 한자 글리프의 세로 범위(3~19행)에 맞춤 (0행까지 쓰면 이웃 칸이 번져 보임)"""
    im = Image.new('L', (cell, cell), 0); dr = ImageDraw.Draw(im)
    _, t, _, b = dr.textbbox((0, 0), '한', font=KO_FONT)     # 기준 높이 고정 (글자마다 흔들리지 않게)
    l, _, r, _ = dr.textbbox((0, 0), ch, font=KO_FONT)
    dr.text(((cell - (r - l)) // 2 - l, round((top + bottom + 1) / 2 - (t + b) / 2)), ch, font=KO_FONT, fill=255)
    a = np.array(im).astype(np.int32)
    return np.clip((a * 3 + 127) // 255, 0, 3)

def build_font(komap, out_path=None, adv=22):
    f = Font(decompress(open(BASE_FONT, 'rb').read()))
    for ch, code in komap.map.items():
        idx = sjis_index(code)
        f.put(idx, render_glyph(ch))
        f.set_width(idx, adv)
    raw = bytes(f.d)
    comp = compress(raw)
    if out_path: open(out_path, 'wb').write(comp)
    return raw, comp

# ---------------- DOL 패치 ----------------
NEW_ADDR = 0x803A1D00          # 원래 ArenaLo
READROM_CALL = 0x80130088      # SJIS 폰트 ROM 읽기 bl __OSReadROM
ARENA_LIS, ARENA_ADDI = 0x8012BA64, 0x8012BA68
ARENA2_LIS, ARENA2_ADDI = 0x8012BA9C, 0x8012BAA0   # 디버거 플래그 경로 (원래 0x8039FCF0)
SJIS_ROM_BASE = 0x1AFF00

def ppc_b(src, dst, link=True):
    off = dst - src
    assert -0x2000000 <= off < 0x2000000
    return (18 << 26) | (off & 0x3FFFFFC) | (1 if link else 0)
def ha_lo(v):
    lo = v & 0xFFFF; hi = (v >> 16) + (1 if lo & 0x8000 else 0)
    return hi & 0xFFFF, lo
def lis(rd, v): return (15 << 26) | (rd << 21) | (v & 0xFFFF)
def addi(rd, ra, v): return (14 << 26) | (rd << 21) | (ra << 16) | (v & 0xFFFF)

def stub_code(font_addr):
    """r3=buf r4=len r5=ROM오프셋 → font_addr+(r5-SJIS_ROM_BASE)에서 복사, r3=1 반환"""
    fh, fl = ha_lo(font_addr); bh, bl_ = ha_lo(SJIS_ROM_BASE)
    w = [
        lis(6, fh), addi(6, 6, fl),                 # r6 = font
        lis(7, bh), addi(7, 7, bl_),                # r7 = rom base
        0x7CE72850,                                 # subf r7, r7, r5
        0x7CC63A14,                                 # add r6, r6, r7
        0x7C8903A6,                                 # mtctr r4
        addi(6, 6, -1), addi(3, 3, -1),
        0x8C060001,                                 # lbzu r0, 1(r6)
        0x9C030001,                                 # stbu r0, 1(r3)
        0x4200FFF8,                                 # bdnz -8
        addi(3, 0, 1),                              # li r3, 1
        0x4E800020,                                 # blr
    ]
    return b''.join(struct.pack('>I', x) for x in w)

def patch_dol(dol_bytes, font_yay0):
    d = bytearray(dol_bytes)
    h = d[:0x100]
    offs = list(struct.unpack('>18I', h[0:0x48])); addrs = list(struct.unpack('>18I', h[0x48:0x90])); sizes = list(struct.unpack('>18I', h[0x90:0xD8]))
    slot = next(i for i in range(7) if sizes[i] == 0)
    code = stub_code(NEW_ADDR + 0x80)
    body = code.ljust(0x80, b'\0') + font_yay0
    assert len(font_yay0) <= 0x4D000, 'font too big: %x' % len(font_yay0)
    body = body.ljust((len(body) + 0x1F) & ~0x1F, b'\0')
    file_off = (len(d) + 0xFF) & ~0xFF
    d = d.ljust(file_off, b'\0') + body
    offs[slot], addrs[slot], sizes[slot] = file_off, NEW_ADDR, len(body)
    d[0:0x48] = struct.pack('>18I', *offs); d[0x48:0x90] = struct.pack('>18I', *addrs); d[0x90:0xD8] = struct.pack('>18I', *sizes)
    def put(addr, word):
        for i in range(18):
            if sizes[i] and addrs[i] <= addr < addrs[i] + sizes[i]:
                o = offs[i] + addr - addrs[i]; d[o:o+4] = struct.pack('>I', word); return
        raise ValueError(hex(addr))
    def get(addr):
        for i in range(18):
            if sizes[i] and addrs[i] <= addr < addrs[i] + sizes[i]:
                o = offs[i] + addr - addrs[i]; return struct.unpack('>I', d[o:o+4])[0]
    # 원본 확인
    assert get(READROM_CALL) == ppc_b(READROM_CALL, 0x80133798)
    assert get(ARENA_LIS) == lis(3, 0x803A) and get(ARENA_ADDI) == addi(3, 3, 0x1D00)
    put(READROM_CALL, ppc_b(READROM_CALL, NEW_ADDR))
    new_arena = (NEW_ADDR + len(body) + 0xFFF) & ~0xFFF
    ah, al = ha_lo(new_arena)
    put(ARENA_LIS, lis(3, ah)); put(ARENA_ADDI, addi(3, 3, al))
    assert get(ARENA2_LIS) == lis(3, 0x803A) and get(ARENA2_ADDI) == addi(3, 3, -0x310)
    put(ARENA2_LIS, lis(3, ah)); put(ARENA2_ADDI, addi(3, 3, al))
    # OSSetArenaLo(0x8012D070): 값이 폰트 섹션 끝보다 작으면 끌어올림 (부트 정보 경로 포함 모든 경우 보호)
    SETLO = 0x8012D070; CLAMP = NEW_ADDR + 0x40
    assert get(SETLO) == 0x906D8678 and get(SETLO + 4) == 0x4E800020   # stw r3,-0x7988(r13); blr
    clamp = [lis(12, ah), addi(12, 12, al),
             0x7C036040,            # cmplw r3, r12
             0x40800008,            # bge +8
             0x7D836378,            # mr r3, r12
             0x906D8678,            # stw r3, -0x7988(r13)
             0x4E800020]            # blr
    o = offs[slot] + (CLAMP - NEW_ADDR)
    d[o:o + 4 * len(clamp)] = b''.join(struct.pack('>I', x) for x in clamp)
    put(SETLO, ppc_b(SETLO, CLAMP, link=False))
    return bytes(d), new_arena

# ---------------- 메뉴 SELT ----------------
def read_selt_raw(data):
    n, nl = struct.unpack('>II', data[4:12]); out = []
    for k in range(n):
        e = 0x10 + k * (0x10 + 4 * nl)
        nm = data[e:e+16].split(b'\0')[0].decode()
        texts = []
        for j in range(nl):
            p = struct.unpack('>I', data[e+16+4*j:e+20+4*j])[0]
            if p == 0: texts.append(None); continue
            w = []
            while True:
                v = struct.unpack('>I', data[p:p+4])[0]; p += 4
                if v == 0: break
                w.append(v)
            texts.append(w)
        out.append((nm, texts))
    return out

def build_selt_raw(entries):
    n = len(entries); nl = len(entries[0][1]); base = 0x10 + n * (0x10 + 4 * nl)
    table = b''; body = b''; off = base
    for nm, texts in entries:
        table += nm.encode().ljust(16, b'\0')
        for w in texts:
            if w is None: table += struct.pack('>I', 0); continue
            bb = b''.join(struct.pack('>I', v) for v in w + [0])
            table += struct.pack('>I', off); body += bb; off += len(bb)
    return b'SELT' + struct.pack('>III', n, nl, 0) + table + body

import re
TOKEN = re.compile(r'\{([0-9a-fA-F]{4}):(\d+)\}')
def encode_menu(text, komap):
    words = []; p = 0
    def chars(s):
        for ch in s:
            if ch == '\n': words.append(0xFFFFFFFF)
            elif ch in komap.map: words.append(0xC0000000 | komap.map[ch])
            elif ord(ch) < 0x80: words.append(0xC0000000 | (ord(ch) << 8))
            else:
                b = ch.encode('shift_jis')
                words.append(0xC0000000 | (b[0] << 8) | b[1] if len(b) == 2 else 0xC0000000 | (b[0] << 8))
    for m in TOKEN.finditer(text):
        chars(text[p:m.start()]); words.append((int(m.group(1), 16) << 16) | int(m.group(2))); p = m.end()
    chars(text[p:])
    return words
