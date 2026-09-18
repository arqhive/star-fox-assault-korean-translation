import struct, collections
U = lambda b, o: struct.unpack('>I', b[o:o+4])[0]
def read_selt(d):
    n, nl = U(d, 4), U(d, 8)
    ents = []
    for k in range(n):
        e = 0x10 + k*(0x10 + 4*nl)
        nm = d[e:e+16].split(b'\0')[0].decode()
        texts = []
        for j in range(nl):
            p = U(d, e+16+4*j); w = []
            while True:
                v = U(d, p); p += 4
                if v == 0: break
                w.append(v)
            texts.append(w)
        ents.append((nm, texts))
    return ents
def sjis_text(w, ruby=False):
    out = []
    for v in w:
        if v == 0xFFFFFFFF: out.append('\n'); continue
        fl, c = v >> 16, v & 0xFFFF
        if fl == 0xC000:
            if c & 0xFF == 0: out.append(chr(c >> 8))
            else: out.append(bytes([c >> 8, c & 0xFF]).decode('shift_jis', 'replace'))
        elif ruby: out.append('{%04x:%d}' % (fl, c))
        else: pass
    return ''.join(out)
def line_widths(w):
    ws = [0]
    for v in w:
        if v == 0xFFFFFFFF: ws.append(0); continue
        if (v >> 24) in (0x00, 0x20): ws[-1] += (v >> 16) & 0xFF
    return ws
