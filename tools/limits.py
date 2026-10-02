# 대사가 그려지는 창마다 한 줄 폭 한계가 다르다. 값의 근거는 일본판 원문이 실제로
# 지킨 폭이며(tools/jpwidth.py 로 SELT 진행폭을 직접 재서 확인), 추정이 아니다.
#   radio 288px — 전투 중 무전 창. 원문 1,800여 줄이 전각 12자(288px)에서 일관되게 끊긴다.
#   wide  528px — 스테이지 종료 대화(공통 대사 0000_3**/0000_4**). 같은 SELT 안에 섞여 있다.
#   demo  576px — 데모·브리핑·무비 자막.
# 과거에는 '한 블록의 항목이 100개를 넘으면 무전(408px)'으로 추정했는데, 무전 창의
# 실제 폭이 288px 이라 그 사이 폭의 줄이 검사를 통과하고도 화면에서 넘쳤다.
LIMITS = {'radio': 288, 'wide': 528, 'demo': 576}

MENU = {'select', 'resvs', 'ressc1', 'ressc2'}   # 본체 ROM 폰트 — 폭·줄 수 제한이 다르다

def window_of(js, name, n_entries):
    """js: translation/ko 파일 이름, name: 대사 이름, n_entries: 그 블록의 항목 수"""
    if js in MENU: return None
    if n_entries <= 100: return 'demo'           # 데모·브리핑 블록은 항목이 적다
    return 'wide' if name[:6] in ('0000_3', '0000_4') else 'radio'

def limit_of(js, name, n_entries):
    w = window_of(js, name, n_entries)
    return LIMITS[w] if w else None
