# Star Fox Assault fpc/pac 트리 파서·직렬화기
# Container: [count, off0..off_count(끝)] 헤더 + 항목들(보통 NPAC)
# NPAC: 'NPAC', total(헤더 0x20 포함, 0x20 정렬), datasize, index, 0*16 + data
import struct
U = lambda b, o: struct.unpack('>I', b[o:o+4])[0]
P = lambda v: struct.pack('>I', v)
def pad(b, n=0x20): return b + b'\0' * (-len(b) % n)

class Leaf:
    def __init__(s, data): s.data = data
    def ser(s): return s.data
class Npac:
    def __init__(s, index, body, empty=False, raw_dsz=None):
        s.index, s.body, s.empty, s.raw_dsz = index, body, empty, raw_dsz
    def ser(s):
        if s.empty:
            tot, dsz = s.body if s.body else (0, 0)
            return b'NPAC' + P(tot) + P(dsz) + P(s.index) + b'\0'*16
        data = s.body.ser()
        return b'NPAC' + P(0x20 + len(pad(data))) + P(len(data)) + P(s.index) + b'\0'*16 + pad(data)
class NpacList:
    def __init__(s, items, tail=b''): s.items, s.tail = items, tail
    def ser(s): return b''.join(i.ser() for i in s.items) + s.tail
class Container:
    def __init__(s, hdrsize, items, tail): s.hdrsize, s.items, s.tail = hdrsize, items, tail
    def ser(s):
        parts = [i.ser() for i in s.items]
        offs = []; o = s.hdrsize
        for p in parts: offs.append(o); o += len(p)
        hdr = P(len(parts)) + b''.join(P(x) for x in offs) + P(o)
        hdr = hdr + b'\0' * (s.hdrsize - len(hdr))
        return hdr + b''.join(parts) + s.tail

def looks_container(d):
    if len(d) < 12: return False
    n = U(d, 0)
    if n == 0 or n > 4096 or 8 + 4*n > len(d): return False
    offs = [U(d, 4 + 4*k) for k in range(n + 1)]
    if offs[0] < 8 + 4*n or offs[0] % 4 or any(b < a for a, b in zip(offs, offs[1:])) or offs[-1] > len(d): return False
    if d[8 + 4*n:offs[0]].strip(b'\0'): return False
    return all(d[o:o+4] == b'NPAC' for o, e in zip(offs, offs[1:]) if e > o)

def parse_body(d):
    # 구조 해석이 원본과 바이트 단위로 일치할 때만 채택, 아니면 통짜 Leaf
    try:
        node = _parse_body(d)
        if node.ser() == d: return node
    except (AssertionError, IndexError, struct.error):
        pass
    return Leaf(d)

def _parse_body(d):
    if d[:4] == b'NPAC':
        return parse_list(d)
    if looks_container(d):
        n = U(d, 0); offs = [U(d, 4 + 4*k) for k in range(n + 1)]
        items = [parse_list(d[a:b]) if b > a else NpacList([]) for a, b in zip(offs, offs[1:])]
        return Container(offs[0], items, d[offs[-1]:])
    return Leaf(d)

def parse_list(d):
    items = []; p = 0
    while p + 0x20 <= len(d) and d[p:p+4] == b'NPAC':
        tot, dsz, idx = U(d, p+4), U(d, p+8), U(d, p+12)
        if tot == 0 or tot == 0xFFFFFFFF:  # 빈 항목 / 공유 텍스처 자리표시자
            items.append(Npac(idx, (tot, dsz), empty=True)); p += 0x20; continue
        body = d[p+0x20:p+0x20+dsz]
        items.append(Npac(idx, parse_body(body)))
        # 원본 패딩이 0x20 정렬과 다르면 보존
        assert p + tot <= len(d) and tot == 0x20 + len(pad(body)), (hex(p), hex(tot), hex(dsz))
        p += tot
    return NpacList(items, d[p:])

def parse_file(d): return parse_body(d)

def walk(node, path=()):
    """(경로, Npac) 순회"""
    if isinstance(node, NpacList):
        for k, it in enumerate(node.items):
            yield path + (k,), it
            if not it.empty: yield from walk(it.body, path + (k,))
    elif isinstance(node, Container):
        for k, it in enumerate(node.items):
            yield from walk(it, path + ('c%d' % k,))
