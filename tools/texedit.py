# 텍스처 한글화 편집 엔진: 글자 지우기/쓰기, CMPR·C4 인코딩, 파일 내 텍스처 교체
import json, hashlib, struct
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from nut import parse_nutc
from gxtex import decode_nut_tex, palette, _rgb565

FONT_PATH = 'C:/Windows/Fonts/malgunbd.ttf'
SS = 4  # 슈퍼샘플링 배율

def text_layer(size_wh, box, text, color, px, align='center', spacing=0, outline=None, valign='center', dy=0):
    """box 안에 text를 그린 RGBA 레이어(원본 크기)"""
    W, H = size_wh
    big = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(big)
    font = ImageFont.truetype(FONT_PATH, int(px * SS))
    x0, y0, x1, y1 = [v * SS for v in box]
    widths = [dr.textbbox((0, 0), ch, font=font)[2] - dr.textbbox((0, 0), ch, font=font)[0] if ch != ' ' else font.size * 0.28 for ch in text]
    sp = spacing * SS
    if spacing == 'fit':
        n = len(text); tw = sum(widths)
        sp = (x1 - x0 - tw) / (n - 1) if n > 1 else 0
    total = sum(widths) + sp * (len(text) - 1)
    if align == 'center': x = x0 + (x1 - x0 - total) / 2
    elif align == 'left': x = x0
    else: x = x1 - total
    asc, desc = font.getmetrics()
    tb = dr.textbbox((0, 0), '가', font=font)
    th = tb[3] - tb[1]
    y = y0 + (y1 - y0 - th) / 2 - tb[1] + dy * SS
    for ch, w in zip(text, widths):
        if ch != ' ':
            l = dr.textbbox((0, 0), ch, font=font)[0]
            if outline:
                oc, ow = outline
                for ox in range(-ow * SS, ow * SS + 1, SS // 2 or 1):
                    for oy in range(-ow * SS, ow * SS + 1, SS // 2 or 1):
                        dr.text((x - l + ox, y + oy), ch, font=font, fill=tuple(oc))
            dr.text((x - l, y), ch, font=font, fill=tuple(color))
        x += w + (sp if ch != ' ' else 0)
    return np.array(big.resize((W, H), Image.LANCZOS))

def over(dst, layer):
    a = layer[..., 3:4].astype(np.float32) / 255
    out = dst.astype(np.float32)
    out[..., :3] = out[..., :3] * (1 - a) + layer[..., :3] * a
    out[..., 3:4] = np.maximum(out[..., 3:4], layer[..., 3:4])
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)

def auto_color(img, box):
    x0, y0, x1, y1 = box; r = img[y0:y1, x0:x1].reshape(-1, 4).astype(int)
    r = r[r[:, 3] > 128]
    lum = r[:, :3].mean(1); top = r[lum >= np.percentile(lum, 95)]
    return tuple(int(v) for v in top[:, :3].mean(0)) + (255,)

def erase(img, box, mode, color=None, thresh=60):
    x0, y0, x1, y1 = box; img = img.copy()
    if mode == 'transparent':
        img[y0:y1, x0:x1] = 0
    elif mode == 'fill':
        img[y0:y1, x0:x1] = color
    elif mode == 'inpaint':   # 밝은(글자) 픽셀을 주변으로 메움
        reg = img[y0:y1, x0:x1]
        lum = reg[..., :3].astype(int).mean(-1)
        base = np.median(lum)
        mask = (np.abs(lum - base) > thresh).astype(np.uint8)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
        rgb = cv2.inpaint(np.ascontiguousarray(reg[..., :3]), mask, 3, cv2.INPAINT_TELEA)
        reg = reg.copy(); reg[..., :3] = rgb
        img[y0:y1, x0:x1] = reg
    return img

def apply_ops(img, ops):
    for op in ops:
        kind = op[0]
        if kind == 'erase':
            _, box, mode, *rest = op
            img = erase(img, box, mode, *rest)
        elif kind == 'text':
            _, box, text, kw = op
            kw = dict(kw); color = kw.pop('color', None) or (255, 255, 255, 255)
            px = kw.pop('px', (box[3] - box[1]) * 0.8)
            img = over(img, text_layer((img.shape[1], img.shape[0]), box, text, color, px, **kw))
        elif kind == 'auto':
            _, region, text, kw = op
            img = retext_auto(img, region, text, **kw)
        elif kind == 'bar':   # 둥근 색 막대 + 글자 (이름표)
            _, box, color = op
            layer = Image.new('RGBA', (img.shape[1] * SS, img.shape[0] * SS), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rounded_rectangle([v * SS for v in box], radius=4 * SS, fill=tuple(color))
            img = over(img, np.array(layer.resize((img.shape[1], img.shape[0]), Image.LANCZOS)))
        elif kind == 'namebar':  # 원래 막대 색으로 둥근 막대를 새로 그리고 글자
            _, text = op
            px_ = img.reshape(-1, 4).astype(int); px_ = px_[(px_[:, 3] > 200) & (px_[:, :3].min(1) < 200)]
            q = (px_[:, :3] // 16)
            vals, cnt = np.unique(q, axis=0, return_counts=True)
            col = tuple(int(v) * 16 + 8 for v in vals[cnt.argmax()]) + (255,)
            img = np.zeros_like(img)
            layer = Image.new('RGBA', (img.shape[1] * SS, img.shape[0] * SS), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rounded_rectangle([0, 5 * SS, img.shape[1] * SS - 1, 21 * SS], radius=5 * SS, fill=col)
            img = over(img, np.array(layer.resize((img.shape[1], img.shape[0]), Image.LANCZOS)))
            img = over(img, text_layer((img.shape[1], img.shape[0]), (0, 0, img.shape[1], img.shape[0]), text, (255, 255, 255, 255), 15, outline=((20, 20, 20, 255), 1)))
        elif kind == 'iconlabel':   # 아이콘 오른쪽 글자를 지우고 아이콘 끝+gap에서 시작, 아이콘 세로 중심에 맞춤
            _, icon_end, icon_rows, text, kw = op
            img = icon_label(img, icon_end, icon_rows, text, **kw)
        elif kind == 'shift':    # x0~x1 열의 내용(아이콘 등)을 dy만큼 세로 이동
            _, (sx0, sx1), sdy = op[:3]; thr = op[3] if len(op) > 3 else 40
            img = shift_content(img, sx0, sx1, sdy, thr)
        elif kind == 'func':    # 사용자 함수로 이미지 변환
            img = op[1](img)
        elif kind == 'paste':   # 다른 영역 복사 (배경 복제)
            _, src, dst = op
            sx0, sy0, sx1, sy1 = src; dx0, dy0 = dst
            img = img.copy(); img[dy0:dy0 + sy1 - sy0, dx0:dx0 + sx1 - sx0] = img[sy0:sy1, sx0:sx1]
    return img

# ---------------- 인코더 ----------------
def enc_c4(img, pal):
    nbx = (img.shape[1] + 7) // 8; nby = (img.shape[0] + 7) // 8
    full = np.zeros((nby * 8, nbx * 8, 4), np.uint8); full[:img.shape[0], :img.shape[1]] = img
    px = full.reshape(-1, 4).astype(int); pp = pal.astype(int)
    d = ((px[:, None, :3] - pp[None, :, :3]) ** 2).sum(-1) * (px[:, None, 3:4].clip(0, 255) / 255 + 0.2)[..., 0] + ((px[:, None, 3] - pp[None, :, 3]) * 3) ** 2
    idx = d.argmin(1).reshape(nby * 8, nbx * 8)
    blk = idx.reshape(nby, 8, nbx, 8).transpose(0, 2, 1, 3).reshape(-1)
    return ((blk[0::2] << 4) | blk[1::2]).astype(np.uint8).tobytes()

def _to565(c):
    r, g, b = [int(v) for v in c[:3]]
    return ((r * 31 + 127) // 255) << 11 | ((g * 63 + 127) // 255) << 5 | ((b * 31 + 127) // 255)

def enc_cmpr(img):
    h, w = img.shape[:2]; nbx = (w + 7) // 8; nby = (h + 7) // 8
    full = np.zeros((nby * 8, nbx * 8, 4), np.uint8); full[:h, :w] = img
    out = bytearray()
    for by in range(nby):
        for bx in range(nbx):
            for sy in range(2):
                for sx in range(2):
                    b = full[by*8 + sy*4:by*8 + sy*4 + 4, bx*8 + sx*4:bx*8 + sx*4 + 4].reshape(16, 4).astype(int)
                    opaque = b[:, 3] >= 128
                    if not opaque.any():
                        out += struct.pack('>HHI', 0, 0xFFFF, 0xFFFFFFFF); continue
                    cols = b[opaque, :3]
                    lum = cols @ np.array([299, 587, 114])
                    hi = cols[lum.argmax()]; lo = cols[lum.argmin()]
                    c0, c1 = _to565(hi), _to565(lo)
                    transparent = not opaque.all()
                    if transparent:
                        if c0 > c1: c0, c1 = c1, c0
                        if c0 == c1 and c1 < 0xFFFF: c1 += 0
                    else:
                        if c0 < c1: c0, c1 = c1, c0
                        if c0 == c1:
                            if c0 > 0: c1 = c0 - 1
                            else: c0 = 1
                    e = _rgb565(np.array([c0, c1])).astype(int)[:, :3]
                    if c0 > c1: pal = [e[0], e[1], (2*e[0] + e[1]) // 3, (e[0] + 2*e[1]) // 3]
                    else: pal = [e[0], e[1], (e[0] + e[1]) // 2, None]
                    bits = 0
                    for k in range(16):
                        if not opaque[k] and pal[3] is None: ii = 3
                        else:
                            cand = [j for j in range(4) if pal[j] is not None]
                            ii = min(cand, key=lambda j: ((b[k, :3] - pal[j]) ** 2).sum())
                        bits = (bits << 2) | ii
                    out += struct.pack('>HHI', c0, c1, bits)
    return bytes(out)

def enc_c8(img, pal, used=None):
    """C8 (이 게임은 8x4 블록), used: 쓸 팔레트 인덱스 목록"""
    nbx = (img.shape[1] + 7) // 8; nby = (img.shape[0] + 3) // 4
    full = np.zeros((nby * 4, nbx * 8, 4), np.uint8); full[:img.shape[0], :img.shape[1]] = img
    cand = np.array(sorted(used)) if used is not None else np.arange(len(pal))
    px = full.reshape(-1, 4).astype(int); pp = pal[cand].astype(int)
    d = ((px[:, None, :3] - pp[None, :, :3]) ** 2).sum(-1) * (px[:, None, 3:4].clip(0, 255) / 255 + 0.2)[..., 0] + ((px[:, None, 3] - pp[None, :, 3]) * 3) ** 2
    idx = cand[d.argmin(1)].reshape(nby * 4, nbx * 8)
    return idx.reshape(nby, 4, nbx, 8).transpose(0, 2, 1, 3).reshape(-1).astype(np.uint8).tobytes()

def encode_like(nd, t, img):
    f = t['fmt']
    if f == 4: return enc_cmpr(img)
    if f == 5:
        pal = palette(nd[t['pal_off']:t['pal_off'] + t['pal']], int(t['b'][4:6], 16))
        return enc_c4(img, pal)
    if f == 6:
        pal = palette(nd[t['pal_off']:t['pal_off'] + t['pal']], int(t['b'][4:6], 16))
        used = set(nd[t['data_off']:t['data_off'] + t['dsz']])
        return enc_c8(img, pal, used)
    raise ValueError('unsupported fmt %d' % f)

# ---------------- 파일 내 텍스처 교체 ----------------
def tex_key(nd, t):
    gid = nd[t['off'] + 0x48:t['off'] + 0x4C].hex()
    blob = nd[t['data_off']:t['data_off'] + t['dsz']] + nd[t['pal_off']:t['pal_off'] + t['pal']]
    return gid, t['w'], t['h'], hashlib.md5(blob).hexdigest()

def patch_textures(data, repl):
    """repl: {(w,h,hash): new_data_bytes} → 교체된 바이트, 교체 수"""
    d = bytearray(data); n = 0; i = -1
    while True:
        i = d.find(b'NUTC', i + 1)
        if i < 0: break
        try: ts = parse_nutc(bytes(d[i:i + 0x800000]))
        except Exception: continue
        for t in ts:
            k = tex_key(bytes(d[i:i + t['pal_off'] + t['pal']]), t)[1:]    # GIDX는 중복·재사용되므로 크기+내용 해시로 비교
            if k in repl:
                nb = repl[k]
                if isinstance(nb, tuple):     # ('entry', 텍스처 항목 전체) — 크기는 원래 tot 유지
                    ent = bytearray(nb[1]); assert len(ent) <= t['tot']
                    ent[0:4] = struct.pack('>I', t['tot']); ent = ent.ljust(t['tot'], b'\0')
                    d[i + t['off']:i + t['off'] + t['tot']] = ent; n += 1
                else:
                    assert len(nb) == t['dsz']
                    d[i + t['data_off']:i + t['data_off'] + t['dsz']] = nb; n += 1
    return bytes(d), n

def detect_text(img, region, thresh=60):
    """영역 안 글자 픽셀 마스크와 경계 상자(원본 좌표)"""
    x0, y0, x1, y1 = region
    reg = img[y0:y1, x0:x1].astype(int)
    lum = reg[..., :3].mean(-1)
    base = np.median(lum)
    mask = (np.abs(lum - base) > thresh) & (reg[..., 3] > 100)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    keep = np.zeros_like(mask)
    rw, rh = x1 - x0, y1 - y0
    for k in range(1, n):
        x, y, w, h, area = stats[k]
        if w >= rw * 0.92 or h >= rh * 0.95: continue          # 테두리 선
        if area <= 1: continue
        keep |= lab == k
    if not keep.any(): return keep, None
    ys, xs = np.nonzero(keep)
    return keep, (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)

def retext_auto(img, region, text, px=None, align='left', color=(255, 255, 255, 255), thresh=40, outline=None, dx=0, spacing=0, color_auto=False, dy=0, x=None):
    mask, bb = detect_text(img, region, thresh)
    assert bb is not None, ('no text found', region)
    x0, y0, x1, y1 = region
    if color_auto: color = auto_color(img, bb)
    m = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    img = img.copy(); reg = img[y0:y1, x0:x1]
    # 인페인팅은 얼룩이 생김 → 같은 줄의 배경(글자 아님, 밝기가 기준값 근처) 중앙값으로 채움
    lum = reg[..., :3].astype(int).mean(-1); base = np.median(lum)
    bgmask = ~m & (np.abs(lum - base) < thresh / 2)
    for yy in range(reg.shape[0]):
        if not m[yy].any(): continue
        src = reg[yy][bgmask[yy]]
        if len(src) < 3:
            near = [r for r in range(reg.shape[0]) if bgmask[r].sum() >= 3]
            if not near: continue
            src = reg[min(near, key=lambda r: abs(r - yy))][bgmask[min(near, key=lambda r: abs(r - yy))]]
        reg[yy, m[yy], :3] = np.median(src[:, :3], axis=0).astype(np.uint8)
    bx0, by0, bx1, by1 = bb
    px = px or (by1 - by0) * 1.05
    cy = (by0 + by1) / 2
    h = max(by1 - by0, px) + 4
    if align == 'left': box = ((x if x is not None else bx0 + dx), int(cy - h / 2), x1, int(cy + h / 2 + 1))
    else: box = (x0, int(cy - h / 2), x1, int(cy + h / 2 + 1))
    return over(img, text_layer((img.shape[1], img.shape[0]), box, text, color, px, align=align, spacing=spacing, outline=outline, dy=dy))

def fill_rows(img, m, x0, x1, thresh=40):
    """m(마스크) 픽셀을 같은 줄 배경 중앙값으로 채움 (x0~x1 범위의 배경 참조)"""
    reg = img[:, x0:x1]; mm = m[:, x0:x1]
    lum = reg[..., :3].astype(int).mean(-1); base = np.median(lum[reg[..., 3] > 100])
    bg = ~mm & (np.abs(lum - base) < thresh / 2) & (reg[..., 3] > 100)
    for y in range(reg.shape[0]):
        if not mm[y].any(): continue
        near = [r for r in range(reg.shape[0]) if bg[r].sum() >= 3]
        if not near: continue
        r = y if bg[y].sum() >= 3 else min(near, key=lambda r: abs(r - y))
        reg[y, mm[y]] = np.median(reg[r][bg[r]], axis=0).astype(np.uint8)
    return img

def icon_label(img, icon_end, icon_rows, text, px=15, gap=5, color=(255, 255, 255, 255), outline=None, thresh=40, right=None, cy=None, minpx=10):
    img = img.copy(); H, W = img.shape[:2]; right = right or W
    a = img[..., 3] > 100
    x0 = icon_end + 1
    if a.mean() > 0.6:     # 불투명 막대: 글자 픽셀만 배경색으로
        lum = img[..., :3].astype(int).mean(-1)
        m = a & (np.abs(lum - np.median(lum[a])) > thresh); m[:, :x0] = False
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool); m[:, :x0] = False
        img = fill_rows(img, m, 0, W, thresh)
    else:
        img[:, x0:] = 0
    cy = cy if cy is not None else (icon_rows[0] + icon_rows[1] + 1) / 2
    h = 24
    while True:
        lay = text_layer((W, H), (icon_end + gap, int(round(cy - h / 2)), 1000, int(round(cy + h / 2))), text, color, px, align='left', outline=outline)
        if not (lay[:, right - 1:, 3] > 60).any() or px <= minpx: break
        px -= 0.5
    return over(img, lay)

def shift_content(img, x0, x1, dy, thresh=40):
    img = img.copy(); H = img.shape[0]; a = img[..., 3] > 100
    if a.mean() > 0.6:
        lum = img[..., :3].astype(int).mean(-1)
        m = a & (np.abs(lum - np.median(lum[a])) > thresh); m[:, :x0] = False; m[:, x1:] = False
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool); m[:, :x0] = False; m[:, x1:] = False
        src = img.copy()
        img = fill_rows(img, m, 0, img.shape[1], thresh)
        ys, xs = np.nonzero(m)
        ny = ys + dy; ok = (ny >= 0) & (ny < H)
        img[ny[ok], xs[ok]] = src[ys[ok], xs[ok]]
    else:
        part = img[:, x0:x1].copy(); img[:, x0:x1] = 0
        if dy < 0: img[:H + dy, x0:x1] = part[-dy:]
        else: img[dy:, x0:x1] = part[:H - dy]
    return img
