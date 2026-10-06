# 대사 문장부호 검수: 평서문 끝에 마침표 추가 (규칙 + 예외 목록)
import json, glob, re, sys, os
import paths

FILES = sorted(paths.KO.glob('s0*.json')) + sorted(paths.KO.glob('s10.json')) + \
        sorted(paths.KO.glob('m*.json')) + sorted(paths.KO.glob('b0*.json'))
END_OK = set('다군네어야지게라아줘나고까냐먼봐마해자데돼와면텨소요죠걸군가록워')   # 평서형 종결 어미 끝 글자
SKIP_LAST = {'서', '만', '핑', '중', '흥', '윽', '음', '기', '피', '코', '스', '니', '리', '이', '히', '히힛'}
EXC = {'0762_0430003', '0301_0120004', '0641_0070001', '0761_0580004', '1062_0210002'}   # 옛 정책(감탄사 예외)용 — 현행 기준은 아래 line_issues
TAIL_SKIP = ('라면', '다면', '으면', '지만', '면서', '해서', '라서')
INTERJ = re.compile(r'[으아어우와앗악야약엑액꺄캬크큭헉흑윽핫하허호후히흐흥부빅삐꿀멍캭왁읏읍웩엉잉옷]{2,}')   # 비명·웃음                # 뒤 문장으로 이어지는 어미

def proposal(ko, en='', name=''):
    s = ko.rstrip()
    if not s or not ('가' <= s[-1] <= '힣'): return ko
    last = s[-1]
    if last in SKIP_LAST or last not in END_OK: return ko
    if len(s.split('\n')[-1].strip()) <= 2: return ko          # 마지막 줄이 한두 글자면 감탄사·호칭
    if '{' in s.split('\n')[-1]: return ko                     # 버튼 아이콘이 든 조작 설명
    if name.startswith('title') or name in EXC: return ko      # 미션 부제·예외 줄
    if s.endswith(TAIL_SKIP): return ko                        # 뒤로 이어지는 어미
    e = en.rstrip().rstrip('"')
    if e.endswith('?') and s[-1] in '가까냐나니': return ko + '?'          # 의문형
    bang = e.endswith('!') and not name.endswith('020')   # 020 = 나우스(로봇) 담담한 보고체
    return ko + ('!' if bang else '.')

def walk(apply=False, exc=()):
    n = 0
    for fn in FILES:
        b = json.load(open(fn, encoding='utf-8')); ch = 0
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl.get('entries', []):
                ko = e.get('ko')
                if not ko: continue
                new = ko if e['name'] in exc else proposal(ko, e.get('en') or '', e['name'])
                if new != ko:
                    n += 1; ch += 1
                    if apply: e['ko'] = new
                    else: print('%s | %s | %s | %s' % (os.path.basename(fn)[:-5], e['name'], ko.replace('\n', '/'), (e.get('en') or '').replace('\n', '/')))
        if apply and ch: json.dump(b, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('총 %d줄' % n, file=sys.stderr)

if __name__ == '__main__':
    walk(apply='--apply' in sys.argv)


# ---- 화자 전환 = 발화 끝: 대사 항목 끝에는 항상 문장부호 ----
def final_pass(apply=False):
    n = 0
    for fn in FILES:
        b = json.load(open(fn, encoding='utf-8')); ch = 0
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl.get('entries', []):
                ko = (e.get('ko') or '').rstrip()
                if not ko or e['name'].startswith('title'): continue
                if not ('가' <= ko[-1] <= '힣'): continue
                if len(ko.replace('\n', ' ').strip()) <= 3: continue      # 감탄사 한 마디
                if '{' in ko.split('\n')[-1]: continue                     # 버튼 조작 안내
                if e['name'] in EXC or ko.endswith(TAIL_SKIP): continue     # 다음 대사로 이어지는 줄
                if INTERJ.fullmatch(ko.split('\n')[-1].strip().replace(' ', '')): continue   # 비명·웃음
                new = ko + '.'
                n += 1
                if apply: e['ko'] = new; ch += 1
                else: print('%-8s %-14s %s' % (os.path.basename(fn)[:-5], e['name'], ko.replace('\n', '/')))
        if apply and ch: json.dump(b, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('대상 %d줄' % n, file=sys.stderr)


# ---- 줄 끝 부호 검사 (check_ko.py 가 파일마다 부른다) ----
# 정책(2026-10-03, 10-06 고침): 한글로 끝나는 대사 끝에는 감탄사·호칭·명사형 보고라도 부호를 찍는다.
# 단 비명·웃음만으로 된 대사(「꺄아아악」「으윽」)와 웃음으로 끝나는 대사(「…큰일 난데이~ 부히히」)에는
# 찍지 않는다(스타폭스 제로 v1.2f 기준을 시리즈에 맞춤). 거꾸로 거기에 마침표가 있으면 걸린다.
# 줄바꿈 앞에서 끝나는 문장도 다음 줄이 새 문장이면 부호를 찍는다(일본어 원문은 줄바꿈이
# 문장 경계라 줄 끝 부호가 없고, 번역이 그 구조를 따라가면 빠진다). 예외는 아래 셋뿐이다.
#   · 다음 대사로 문장이 이어지는 항목(CONT)            「…아파로이드에게」→「함대가 괴멸당했지…」
#   · 호칭만 있는 다음 줄 앞(줄바꿈이 쉼표 역할, 관례)  「괜찮냐 / 폭스!」
#   · 미션 제목·조작 안내 라벨·선택지                   「길게 누르기」「예」
# 줄 중간은 연결(…때까지 / …하다니)과 문장 끝을 규칙만으로 가를 수 없어, 종결 어미로 끝나는
# 줄을 후보로 뽑고 사람이 확인한 「이어지는 줄」은 data/punct_mid_ok.json 에 둔다.
# 번역이 바뀌면 줄 내용이 달라져 다시 후보가 된다.
CONT = {'0201_0110007', '0301_0070027', '0301_0120004', '0601_0030005', '0701_0020006',
        '0901_0050001', '0901_0080005', '0361_2180004'}
LABELS = {'mes_d05', 'mes_d06'}                       # 예 / 아니요
SKIP_FILES = {'select', 'resvs', 'ressc1', 'ressc2'}  # 메뉴(ROM 폰트) — 항목 이름·라벨
END_CH = set('다군해냐어자야까네아지라나요죠걸데게고니든봐줘와래')   # 종결 어미가 될 수 있는 끝 글자
JOIN_WORD = ('장군', '보다', '마다', '바다', '하고', '이고', '되고', '있고', '없고', '하게', '있게', '없게',
             '되게', '는데', '은데', '인데', '한데', '던데', '하지', '되지', '않지', '하니', '되니', '으니',
             '이니', '어서', '해서', '라도', '이라', '다가', '도록', '지만', '라나')
VOC_LINE = re.compile(r'(폭스|팔코|페피|슬리피|크리스탈|다들|폭스, 다들|팔코, 슬리피)[!?.~…]*')
# 비명·웃음: 한 줄 전체가 의성 음절뿐이거나, 줄 끝이 웃음소리
SCREAM_LINE = re.compile(r'[…~ ]*[으아악어우와꺄캬크큭끄끼히이익윽흐흑헉하허호후부핫힛읏엑켁깨갱]+[~!?… ]*')
LAUGH_END = re.compile(r'(하하|히히|후후|부히히|부히힛|와하하|헤헤|크크)[하히후힛헤크]*[~!?…]*$')

def is_scream(last):
    t = last.strip().rstrip('.')
    return bool(t) and (SCREAM_LINE.fullmatch(t) is not None or LAUGH_END.search(t) is not None)

_MID_OK = None

def _mid_ok():
    global _MID_OK
    if _MID_OK is None:
        p = paths.DATA / 'punct_mid_ok.json'
        _MID_OK = {tuple(x) for x in json.load(open(str(p), encoding='utf-8'))} if p.exists() else set()
    return _MID_OK

def mid_candidates(js, name, ko):
    """부호 없이 종결 어미로 끝나는 중간 줄 (줄 번호, 줄 내용)"""
    out = []
    L = ko.split('\n')
    for i, l in enumerate(L[:-1]):
        t = l.rstrip()
        if not t or not ('가' <= t[-1] <= '힣'): continue
        if i == 0 and js.startswith('b'): continue                # 브리핑 첫 줄은 화자 이름표
        nxt = L[i + 1].strip()
        if VOC_LINE.fullmatch(nxt): continue                     # 호칭 앞 줄바꿈
        if not nxt.startswith('{') and (t[-1] not in END_CH or t.endswith(JOIN_WORD)): continue
        out.append((i, t))
    return out

def line_issues(js, name, ko):
    if js in SKIP_FILES or name in LABELS or name.startswith('title'): return []
    out = []
    s = ko.rstrip(); last = s.split('\n')[-1]
    if is_scream(last):
        if s.endswith('.'): out.append('비명·웃음 뒤 마침표: %s' % s.replace('\n', '/'))
    elif s and '가' <= s[-1] <= '힣' and '{' not in last and name not in CONT:
        out.append('대사 끝 부호 없음: %s' % s.replace('\n', '/'))
    ok = _mid_ok()
    for i, t in mid_candidates(js, name, ko):
        if (name, t) in ok: continue
        out.append('%d번째 줄 끝 부호 확인(검토 후 data/punct_mid_ok.json 에 등록): %s' % (i + 1, ko.replace('\n', '/')))
    return out

def save_mid_ok():
    """현재 남은 중간 줄 후보를 전부 「이어지는 줄」로 등록한다 — 전수 검토를 마친 뒤에만 쓴다."""
    rows = set()
    for fn in paths.KO.glob('*.json'):
        if fn.stem in SKIP_FILES: continue
        b = json.load(open(str(fn), encoding='utf-8'))
        for bl in (b if isinstance(b, list) else [b]):
            for e in bl['entries']:
                for i, t in mid_candidates(fn.stem, e['name'], e.get('ko') or ''): rows.add((e['name'], t))
    json.dump(sorted(rows), open(str(paths.DATA / 'punct_mid_ok.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('등록 %d줄' % len(rows))
