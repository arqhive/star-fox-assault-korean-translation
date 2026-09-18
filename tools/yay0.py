import struct
def decompress(src):
    assert src[:4] == b'Yay0'
    size, link, chunk = struct.unpack('>III', src[4:16])
    out = bytearray(); mp = 16; lp = link; cp = chunk; mask = 0; bits = 0
    while len(out) < size:
        if bits == 0:
            mask = struct.unpack('>I', src[mp:mp+4])[0]; mp += 4; bits = 32
        if mask & 0x80000000:
            out.append(src[cp]); cp += 1
        else:
            v = struct.unpack('>H', src[lp:lp+2])[0]; lp += 2
            dist = (v & 0xfff) + 1; n = v >> 12
            if n == 0: n = src[cp] + 18; cp += 1
            else: n += 2
            for _ in range(n): out.append(out[-dist])
        mask = (mask << 1) & 0xffffffff; bits -= 1
    return bytes(out)
def compress(data):
    """단순 LZ(해시 탐색) Yay0 압축"""
    masks = []; links = bytearray(); chunks = bytearray()
    cur = 0; bits = 0; nbits = 0
    table = {}
    i = 0; n = len(data)
    def flag(b):
        nonlocal cur, nbits
        cur = (cur << 1) | b; nbits += 1
        if nbits == 32: masks.append(cur); cur = 0; nbits = 0
    while i < n:
        best_len = 0; best_d = 0
        if i + 3 <= n:
            key = data[i:i+3]
            for j in reversed(table.get(key, [])[-32:]):
                d = i - j
                if d > 0x1000: continue
                l = 3; mx = min(0x111, n - i)
                while l < mx and data[j+l] == data[i+l]: l += 1
                if l > best_len: best_len, best_d = l, d
                if l == mx: break
        if best_len >= 3:
            flag(0)
            if best_len <= 17:
                links += struct.pack('>H', ((best_len - 2) << 12) | (best_d - 1))
            else:
                links += struct.pack('>H', best_d - 1); chunks.append(best_len - 18)
            for k in range(i, i + best_len):
                if k + 3 <= n: table.setdefault(data[k:k+3], []).append(k)
            i += best_len
        else:
            flag(1); chunks.append(data[i])
            if i + 3 <= n: table.setdefault(data[i:i+3], []).append(i)
            i += 1
    if nbits: masks.append(cur << (32 - nbits))
    mbytes = b''.join(struct.pack('>I', m) for m in masks)
    link_off = 16 + len(mbytes); chunk_off = link_off + len(links)
    return b'Yay0' + struct.pack('>III', n, link_off, chunk_off) + mbytes + bytes(links) + bytes(chunks)
