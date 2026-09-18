import struct
def parse_nutc(d):
    assert d[:4] == b'NUTC'
    n = struct.unpack('>H', d[6:8])[0]
    p = 0x20; out = []
    for i in range(n):
        tot, pal, dsz, hsz = struct.unpack('>IIIH', d[p:p+14])
        b = d[p+0x10:p+0x18]
        mip, fmt = b[1], b[3]
        w, h = struct.unpack('>HH', d[p+0x14:p+0x18])
        data = d[p+hsz:p+hsz+dsz]; palette = d[p+hsz+dsz:p+hsz+dsz+pal]
        out.append(dict(i=i, off=p, tot=tot, pal=pal, dsz=dsz, hsz=hsz, b=b.hex(), mip=mip, fmt=fmt, w=w, h=h, data_off=p+hsz, pal_off=p+hsz+dsz))
        p += tot
    return out
