# 대사 문장부호 검수: 평서문 끝에 마침표 추가 (규칙 + 예외 목록)
import json, glob, re, sys, os
import paths

FILES = sorted(paths.KO.glob('s0*.json')) + sorted(paths.KO.glob('s10.json')) + \
        sorted(paths.KO.glob('m*.json')) + sorted(paths.KO.glob('b0*.json'))
END_OK = set('다군네어야지게라아줘나고까냐먼봐마해자데돼와면텨소요죠걸군가록워')   # 평서형 종결 어미 끝 글자
SKIP_LAST = {'서', '만', '핑', '중', '흥', '윽', '음', '기', '피', '코', '스', '니', '리', '이', '히', '히힛'}
EXC = {'0762_0430003', '0301_0120004', '0641_0070001', '0761_0580004', '1062_0210002'}   # 이어지는 말·감탄사로 끝나 마침표가 어색한 줄
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
