import struct
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN
class Dol:
    def __init__(s, path):
        d = s.data = open(path, 'rb').read()
        h = d[:0x100]
        off = struct.unpack('>18I', h[0:0x48]); addr = struct.unpack('>18I', h[0x48:0x90]); size = struct.unpack('>18I', h[0x90:0xD8])
        s.secs = [(i, off[i], addr[i], size[i]) for i in range(18) if size[i]]
        s.bss = struct.unpack('>II', h[0xD8:0xE0]); s.entry = struct.unpack('>I', h[0xE0:0xE4])[0]
        s.md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN); s.md.detail = False
    def a2o(s, a):
        for i, o, ad, sz in s.secs:
            if ad <= a < ad + sz: return o + a - ad
    def o2a(s, o):
        for i, of, ad, sz in s.secs:
            if of <= o < of + sz: return ad + o - of
    def u32(s, a): return struct.unpack('>I', s.data[s.a2o(a):s.a2o(a)+4])[0]
    def text(s): return [(ad, s.data[o:o+sz]) for i, o, ad, sz in s.secs if i < 7]
    def dis(s, a, n=40):
        o = s.a2o(a); return list(s.md.disasm(s.data[o:o+4*n], a))
    def words(s):
        for ad, b in s.text():
            for k in range(0, len(b), 4):
                yield ad + k, struct.unpack('>I', b[k:k+4])[0]

def lis_addi_refs(d, targets, window=12):
    """lis rX,hi ; (addi|ori|lwz|lbz...) rY,lo(rX) 로 만들어지는 주소 → 명령 위치"""
    ws = list(d.words()); out = {}
    for n, (a, w) in enumerate(ws):
        if (w >> 26) == 15 and ((w >> 16) & 0x1f) == 0:
            rd = (w >> 21) & 0x1f; hi = w & 0xffff
            for m in range(n + 1, min(n + window, len(ws))):
                a2, w2 = ws[m]; op = w2 >> 26
                if ((w2 >> 16) & 0x1f) == rd and op in (14, 24, 32, 34, 36, 38, 40, 44, 48, 52, 54):
                    lo = w2 & 0xffff
                    val = ((hi << 16) + (lo - 0x10000 if (op != 24 and lo & 0x8000) else lo)) & 0xffffffff
                    if val in targets: out.setdefault(val, []).append(a2)
                    break
    return out
