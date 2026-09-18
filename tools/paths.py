# 저장소 안팎 경로 (어느 폴더에서 실행해도 같게 동작)
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / 'tools'
DATA = TOOLS / 'data'                 # 텍스처 목록(오프셋·해시)
TRANS = ROOT / 'translation'
KO = TRANS / 'ko'                     # 번역 JSON
DRAFTS = TRANS / 'drafts'             # 번역 원고(.py)
RELEASE = ROOT / 'release'
WORK = ROOT / 'work'                  # 빌드 결과·원문 등 커밋하지 않는 작업 폴더

def _find(env, *names):
    p = os.environ.get(env)
    if p: return Path(p)
    for d in (ROOT, ROOT / 'iso', ROOT.parent):
        for n in names:
            if (d / n).exists(): return d / n
    raise FileNotFoundError('%s 를 찾을 수 없습니다 (환경 변수 %s 로 지정하세요)' % (names[0], env))

def jp_iso(): return str(_find('SFA_JP_ISO', 'Star Fox - Assault (Japan).iso'))
def us_iso(): return str(_find('SFA_US_ISO', 'Star Fox - Assault (USA).iso'))
def gc_font():
    p = os.environ.get('GC_FONT_JAPANESE')
    if p: return p
    for d in (ROOT.parent / 'Dolphin-x64', ROOT.parent.parent / 'Dolphin-x64'):
        f = d / 'Sys' / 'GC' / 'font_japanese.bin'
        if f.exists(): return str(f)
    return str(ROOT.parent / 'Dolphin-x64' / 'Sys' / 'GC' / 'font_japanese.bin')
