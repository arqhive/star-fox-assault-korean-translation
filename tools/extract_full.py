# 일본판·북미판 ISO에서 대사 원문을 다시 뽑아 번역과 합친다 → work/text_full/<파일>.json
#   python tools/extract_full.py   (ISO 두 벌은 저장소 루트·iso/·상위 폴더, 또는 SFA_JP_ISO·SFA_US_ISO)
# 일본판 대사는 장면별 글자 그림 번호로만 들어 있어 글자를 읽을 수 없으므로, 북미판에 남아 있는
# 일본어 원문(lang0)을 일본판 대사 이름 기준으로 맞춘다(extract_text2.py). 결과 항목:
# name·speaker·jp·en·ko. 원문이 들어 있으니 git 에 넣지 않는다(work/ 는 git 제외).
# 화자 번호는 대사 이름 끝 세 자리(docs/REVIEW_GUIDE.md 표). 문체 재검수(v1.2.1f)에 썼다.
import sys, json, subprocess, os
from pathlib import Path
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / 'tools'))
import paths
from gcfs import read_fst
JP, US = paths.jp_iso(), paths.us_iso()
TARGETS = [('/movie/m0111.fpc','m0111'),('/movie/m0121.fpc','m0121'),
    ('/fpc/s_01_01.fpc','s01'),('/fpc/s_02_01.fpc','s02'),('/fpc/s_03_01.fpc','s03'),('/fpc/s_04_01.fpc','s04'),
    ('/movie/m0541.fpc','m0541'),('/fpc/s_05_01.fpc','s05'),('/movie/m0641.fpc','m0641'),('/fpc/s_06_01.fpc','s06'),
    ('/fpc/s_07_01.fpc','s07'),('/fpc/s_08_01.fpc','s08'),('/movie/m3100.fpc','m3100'),('/fpc/s_09_01.fpc','s09'),
    ('/movie/m3200.fpc','m3200'),('/fpc/s_10_01.fpc','s10'),('/movie/m1041.fpc','m1041'),('/movie/m2300.fpc','m2300')] + \
    [('/fpc/b0%d01.fpc' % i, 'b0%d' % i) for i in range(1, 10)]
def dump(iso, tag):
    f, gid, name, dol, ents = read_fst(iso); loc = {p: (o, s) for p, o, s in ents}
    d = R / 'work' / ('orig_' + tag); d.mkdir(parents=True, exist_ok=True)
    for p, _ in TARGETS:
        if p not in loc: print(tag, '없음', p); continue
        f.seek(loc[p][0]); (d / p.strip('/').replace('/', '__')).write_bytes(f.read(loc[p][1]))
    f.close(); return d
dj, du = dump(JP, 'jp'), dump(US, 'us')
us_all = sorted(str(x) for x in du.iterdir())
out = R / 'work' / 'text_full'; out.mkdir(exist_ok=True)
for p, js in TARGETS:
    jf, uf = dj / p.strip('/').replace('/', '__'), du / p.strip('/').replace('/', '__')
    tmp = out / (js + '.raw.json')
    r = subprocess.run([sys.executable, str(R / 'tools' / 'extract_text2.py'), str(jf), str(uf), str(tmp)] + [x for x in us_all if x != str(uf)],
                       capture_output=True, text=True, encoding='utf-8', cwd=str(R / 'tools'))
    if r.returncode: print(js, '실패', r.stderr[-400:]); continue
    blocks = json.load(open(tmp, encoding='utf-8')); tmp.unlink()
    ko = json.load(open(R / 'translation' / 'ko' / (js + '.json'), encoding='utf-8'))
    assert len(ko) == len(blocks), (js, len(ko), len(blocks))
    miss = 0
    for bl, kb in zip(blocks, ko):
        km = {e['name']: e['ko'] for e in kb['entries']}
        for e in bl['entries']:
            e['ko'] = km.get(e['name'], '');  miss += not e['ko']
    json.dump(blocks, open(out / (js + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(js, sum(len(b['entries']) for b in blocks), '줄', '번역 없음', miss)
