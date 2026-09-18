import struct
import numpy as np
from yay0 import decompress
class Font:
    def __init__(s, raw):
        s.d = bytearray(raw)
        (s.type, s.first, s.last, s.inval, s.ascent, s.descent, s.width, s.leading, s.cw, s.ch) = struct.unpack('>10H', raw[:20])
        s.sheetSize, = struct.unpack('>I', raw[20:24])
        s.sfmt, s.cols, s.rows, s.sw, s.sh = struct.unpack('>5H', raw[24:34])
        s.wtab, s.simg, s.sfull = struct.unpack('>HII', raw[34:44])
        s.pal = raw[44:48]
    def nglyph(s): return (len(s.d) - s.simg) // (s.sw * s.sh // 4) * s.cols * s.rows
    def cell(s, idx):
        per = s.cols * s.rows; sheet, k = divmod(idx, per); r, c = divmod(k, s.cols)
        return sheet, c * s.cw, r * s.ch
    def sheet_px(s, sheet):
        bpsheet = s.sw * s.sh // 4
        b = np.frombuffer(bytes(s.d[s.simg + sheet*bpsheet: s.simg + (sheet+1)*bpsheet]), np.uint8)
        px = np.stack([(b >> 6) & 3, (b >> 4) & 3, (b >> 2) & 3, b & 3], 1).reshape(-1)
        bpr = s.sw // 8
        return px.reshape(s.sh // 8, bpr, 8, 8).transpose(0, 2, 1, 3).reshape(s.sh, s.sw)
    def get(s, idx):
        sh, x, y = s.cell(idx); return s.sheet_px(sh)[y:y+s.ch, x:x+s.cw]
    def put(s, idx, g2):   # g2: ch x cw 값 0..3
        sh, x, y = s.cell(idx); bpsheet = s.sw * s.sh // 4
        base = s.simg + sh * bpsheet
        for yy in range(s.ch):
            for xx in range(s.cw):
                X, Y = x + xx, y + yy
                blk = (Y // 8) * (s.sw // 8) + X // 8
                p = blk * 64 + (Y % 8) * 8 + (X % 8)
                o = base + p // 4; sft = 6 - 2 * (p % 4)
                s.d[o] = (s.d[o] & ~(3 << sft)) | (int(g2[yy, xx]) << sft)
    def set_width(s, idx, w): s.d[s.wtab + idx] = w
    def get_width(s, idx): return s.d[s.wtab + idx]
def sjis_index(code):
    hi, lo = code >> 8, code & 0xff
    j = lo - 0x40
    if j >= 0x40: j -= 1
    if 0x889F <= code <= 0x9872:
        return (hi - 0x88) * 188 + j + 0x2BE
    return None
