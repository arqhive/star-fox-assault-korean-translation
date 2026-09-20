import numpy as np, struct
def _rgb5a3(v):
    v = v.astype(np.int32)
    hi = (v & 0x8000) != 0
    r = np.where(hi, ((v >> 10) & 31) * 255 // 31, ((v >> 8) & 15) * 17)
    g = np.where(hi, ((v >> 5) & 31) * 255 // 31, ((v >> 4) & 15) * 17)
    b = np.where(hi, (v & 31) * 255 // 31, (v & 15) * 17)
    a = np.where(hi, 255, ((v >> 12) & 7) * 255 // 7)
    return np.stack([r, g, b, a], -1).astype(np.uint8)
def _rgb565(v):
    v = v.astype(np.int32)
    return np.stack([((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31, np.full_like(v, 255)], -1).astype(np.uint8)
def _ia8(v):
    v = v.astype(np.int32); i = v & 255; a = v >> 8
    return np.stack([i, i, i, a], -1).astype(np.uint8)
def palette(pal_bytes, fmt):
    v = np.frombuffer(pal_bytes, '>u2')
    return {0: _ia8, 1: _rgb565, 2: _rgb5a3}[fmt](v)
def blocks(arr, w, h, bw, bh):
    """블록 순서로 저장된 픽셀 배열(블록 개수 x bh x bw x C) → 이미지"""
    nbx = (w + bw - 1) // bw; nby = (h + bh - 1) // bh
    a = arr.reshape(nby, nbx, bh, bw, -1).transpose(0, 2, 1, 3, 4).reshape(nby * bh, nbx * bw, -1)
    return a[:h, :w]
def decode_c4(data, w, h, pal):
    nbx = (w + 7) // 8; nby = (h + 7) // 8
    b = np.frombuffer(data[:nbx * nby * 32], np.uint8)
    idx = np.stack([b >> 4, b & 15], 1).reshape(-1)
    return blocks(pal[idx], w, h, 8, 8)
def decode_c8(data, w, h, pal):
    nbx = (w + 7) // 8; nby = (h + 3) // 4       # 이 게임의 C8은 8x4 블록 (실측)
    idx = np.frombuffer(data[:nbx * nby * 32], np.uint8)
    return blocks(pal[idx], w, h, 8, 4)
def decode_i4(data, w, h):
    nbx = (w + 7) // 8; nby = (h + 7) // 8
    b = np.frombuffer(data[:nbx * nby * 32], np.uint8)
    i = (np.stack([b >> 4, b & 15], 1).reshape(-1) * 17).astype(np.uint8)
    return blocks(np.stack([i, i, i, np.full_like(i, 255)], -1), w, h, 8, 8)
def decode_i8(data, w, h):
    nbx = (w + 7) // 8; nby = (h + 7) // 8
    i = np.frombuffer(data[:nbx * nby * 64], np.uint8)
    return blocks(np.stack([i, i, i, np.full_like(i, 255)], -1), w, h, 8, 8)
def decode_ia4(data, w, h):
    nbx = (w + 7) // 8; nby = (h + 7) // 8
    b = np.frombuffer(data[:nbx * nby * 64], np.uint8)
    a = (b >> 4) * 17; i = (b & 15) * 17
    return blocks(np.stack([i, i, i, a], -1).astype(np.uint8), w, h, 8, 8)
def decode_cmpr(data, w, h):
    nbx = (w + 7) // 8; nby = (h + 7) // 8
    out = np.zeros((nby * 8, nbx * 8, 4), np.uint8); p = 0
    for by in range(nby):
        for bx in range(nbx):
            for sy in range(2):
                for sx in range(2):
                    c0, c1, bits = struct.unpack('>HHI', data[p:p+8]); p += 8
                    cols = _rgb565(np.array([c0, c1])).astype(np.int32)
                    if c0 > c1:
                        c2 = (2 * cols[0] + cols[1]) // 3; c3 = (cols[0] + 2 * cols[1]) // 3; c2[3] = c3[3] = 255
                    else:
                        c2 = (cols[0] + cols[1]) // 2; c2[3] = 255; c3 = np.array([0, 0, 0, 0])
                    pal = np.array([cols[0], cols[1], c2, c3], np.uint8)
                    for y in range(4):
                        for x in range(4):
                            out[by*8 + sy*4 + y, bx*8 + sx*4 + x] = pal[(bits >> (30 - 2 * (y * 4 + x))) & 3]
    return out[:h, :w]

def decode_nut_tex(nd, t, fmt4='cmpr', fmt10='ia4'):
    data = nd[t['data_off']:t['data_off'] + t['dsz']]
    w, h, f = t['w'], t['h'], t['fmt']
    palfmt = int(t['b'][4:6], 16)
    if f == 3: return decode_rgba8(data, w, h)
    if f == 4: return decode_cmpr(data, w, h) if fmt4 == 'cmpr' else decode_i4(data, w, h)
    if f in (5, 6):
        n = 16 if f == 5 else 256
        pal = palette(nd[t['pal_off']:t['pal_off'] + t['pal']], palfmt)
        if len(pal) < n: pal = np.concatenate([pal, np.zeros((n - len(pal), 4), np.uint8)])
        return decode_c4(data, w, h, pal) if f == 5 else decode_c8(data, w, h, pal)
    if f == 10: return decode_ia4(data, w, h) if fmt10 == 'ia4' else decode_i8(data, w, h)
    return None

def decode_rgba8(data, w, h):
    nbx = (w + 3) // 4; nby = (h + 3) // 4
    # GX RGBA8: each 4x4 tile has 32 bytes of AR, then 32 bytes of GB.
    b = np.frombuffer(data[:nbx * nby * 64], np.uint8).reshape(-1, 64)
    a = np.stack([b[:, 1:32:2], b[:, 32:64:2], b[:, 33:64:2], b[:, 0:32:2]], -1)
    return blocks(a, w, h, 4, 4)
