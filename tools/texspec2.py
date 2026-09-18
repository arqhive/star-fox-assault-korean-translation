# 텍스처 한글화 사양 2차: 전수 스캔(scanA/B/C/D.json)에서 찾은 추가 텍스처
import numpy as np
from texedit import text_layer, over
from texspec import A, BLK1, W

SPEC2 = {}
# select.fpc 라벨
SPEC2[('A', 17)] = [('iconlabel', 30, (3, 19), '룰 변경', dict(px=15))]
def boxlabel(w, h, s, px=13):
    return [('erase', (0, 0, w, h), 'fill', (0, 0, 0, 255)), ('text', (0, 0, w, h), s, dict(px=px))]
for ref, w, s in [(('A', 44), 88, '없음'), (('A', 46), 88, '대'), (('A', 105), 80, '없음'), (('A', 106), 80, '있음'),
                  (('A', 108), 80, '포인트'), (('A', 109), 80, '서바이벌'), (('A', 110), 80, '타임')]:
    SPEC2[ref] = boxlabel(w, 16, s)
SPEC2[('A', 73)] = [('erase', (0, 0, 64, 24), 'transparent'), ('text', (0, 0, 64, 24), '누르기', dict(px=15, align='left', outline=BLK1))]
SPEC2[('A', 80)] = [('erase', (0, 0, 136, 32), 'transparent'), ('text', (0, 0, 136, 32), '안 함', dict(px=19))]
SPEC2[('A', 81)] = [('erase', (0, 0, 136, 32), 'transparent'), ('text', (0, 0, 136, 32), '함', dict(px=19))]
for ref, s in [(('A', 82), '1스틱 조작'), (('A', 83), '2스틱 조작'), (('A', 84), '액셀 조작')]:
    SPEC2[ref] = [('erase', (0, 0, 144, 24), 'transparent'), ('text', (0, 0, 144, 24), s, dict(px=18))]
SPEC2[('D', 5)] = [('erase', (0, 0, 112, 34), 'transparent'), ('text', (0, 0, 112, 34), '엔트리', dict(px=22))]
# 결과 화면
SPEC2[('C', 30)] = [('erase', (0, 0, 280, 32), 'fill', (0, 0, 0, 255)),
                    ('text', (0, 0, 280, 32), '축하합니다!!', dict(px=22, color=(110, 225, 205, 255), outline=((230, 245, 245, 255), 1)))]
# 무전 이름표 (80x32, 기울어진 막대)
def relabel(s):
    def f(img):
        img = img.copy(); op = img[..., 3] > 100
        white = op & (img[..., :3].min(-1) > 200)
        bar = op & ~white & (img[..., :3].max(-1) > 50)
        ys, xs = np.nonzero(bar)
        col = np.median(img[ys, xs], axis=0).astype(np.uint8)
        for y in range(ys.min(), ys.max() + 1):
            xb = xs[ys == y]
            if len(xb): img[y, xb.min():xb.max() + 1] = col
        lay = text_layer((img.shape[1], img.shape[0]), (14, ys.min(), 74, ys.max() + 1), s, (255, 255, 255, 255), 13 if len(s) < 4 else 12)
        return over(img, lay)
    return f
for ref, s in [(('B', 9), '팔코'), (('B', 11), '크리스탈'), (('B', 13), '레온'), (('B', 15), '팬서'), (('B', 17), '슬리피'), (('B', 19), '울프')]:
    SPEC2[ref] = [('func', relabel(s))]

# 무전 화자 이름 목록 (C8 96x400, 16px 줄 25개): 검은 글자 + 초록 테두리
RADIO_NAMES = ['폭스', '팔코', '크리스탈', '슬리피', '페피', '나우스', '페퍼 장군', '벨티노', '울프', '팬서', '레온', '피그마',
               None, '오이코니', '트리키', '사령관', '통신병', '코네리아 병사', '내비게이터', '안내 방송', '불량배',
               '오이코니 병사', '마더', '경비 로봇']
def radio_names(img):
    """게임이 줄을 축소해 그리므로 16px 줄을 꽉 채우고 가로로 약간 넓힘"""
    from PIL import Image as _I, ImageDraw as _D, ImageFont as _F
    img = img.copy(); S = 8
    font = _F.truetype('C:/Windows/Fonts/malgunbd.ttf', 16 * S)
    for r, s in enumerate(RADIO_NAMES):
        if s is None: continue
        y = r * 16
        big = _I.new('L', (1200, 32 * S), 0); d = _D.Draw(big)
        d.text((4 * S, 4 * S), s, font=font, fill=255)
        l, t, rr, b = big.getbbox(); big = big.crop((l, t, rr, b))
        h = 14; w = min(92, round(big.width * h / big.height * 1.2))
        core = np.array(big.resize((w, h), _I.LANCZOS))
        a = np.zeros((16, 96), np.float32); a[1:15, 2:2 + w] = core / 255
        import cv2
        ol = cv2.dilate(a, np.ones((3, 3), np.uint8))
        out = np.zeros((16, 96, 4), np.uint8)
        out[..., 1] = (205 * (1 - a)).astype(np.uint8); out[..., 0] = out[..., 2] = (16 * (1 - a)).astype(np.uint8)
        out[..., 3] = (np.maximum(ol, a) * 255).astype(np.uint8)
        img[y:y + 16] = out
    return img
SPEC2[('D', 1)] = [('func', radio_names)]

# 이름 입력 글자 종류 탭 "あ ア A 1" → "가 파 A 1" (한글 음절표 2장의 첫 글자)
SPEC2[('A', 57)] = [('erase', (28, 0, 110, 24), 'fill', (0, 0, 0, 255)),
                    ('text', (30, 0, 56, 24), '가', dict(px=17)), ('text', (81, 0, 107, 24), '파', dict(px=17))]
