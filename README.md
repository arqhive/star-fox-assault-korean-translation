# 스타폭스 어썰트 한글화 (GameCube, 일본판 기반)

일본판 `Star Fox: Assault`(GF7J01)를 한국어로 옮기는 도구와 번역 데이터입니다.
게임 이미지(ISO)는 포함하지 않으며, 직접 가진 일본판 ISO에서 한글판 ISO를 만들어 냅니다.

현재 상태: 스토리(미션 1~10 무전·데모, 무비 자막, 브리핑), 메뉴 텍스트, 주요 그래픽 라벨 한글화 완료 — 테스트판 v0.9 배포.

## 패치 받기

[릴리스](../../releases)에서 `StarFoxAssault_KO_v0.9.xdelta`를 받아 일본판 ISO에 적용하세요.
적용 방법과 해시는 [release/README_한국어.txt](release/README_한국어.txt)에 있습니다.

| | CRC32 | MD5 |
|---|---|---|
| 일본판 ISO | `089208F3` | `27aed37f24061b1ff06cdd3640053481` |
| 패치 적용 결과 | `B56FD8AF` | `23d7d72c15723968db4d3076ba9a0883` |

## 준비물

| 파일 | 위치 | 비고 |
|---|---|---|
| `Star Fox - Assault (Japan).iso` | 저장소 루트 | MD5 `27aed37f24061b1ff06cdd3640053481` (RVZ → ISO 변환본) |
| `Star Fox - Assault (USA).iso` | 저장소 루트 | MD5 `992e00b7df1960d4ca03c76801502f91` — 타이틀 로고만 가져옴 |
| Dolphin `Sys/GC/font_japanese.bin` | 기본 `../Dolphin-x64/Sys/GC/` | 경로가 다르면 환경 변수 `GC_FONT_JAPANESE`로 지정 |
| 맑은 고딕 Bold | `C:/Windows/Fonts/malgunbd.ttf` | 한글 글리프 렌더링 |
| Python 3.11+ | | `pip install -r tools/requirements.txt` |

## 빌드

```bash
cd tools
python build_all.py "../Star Fox - Assault [KO].iso"
```

일본판 ISO를 읽어 변경 파일(약 58개)과 패치된 DOL로 ISO를 다시 구성하고, 1090개 파일 전부를 검증합니다.
Windows Git Bash에서는 `MSYS_NO_PATHCONV=1`, `PYTHONIOENCODING=utf-8`을 지정하세요.
같은 입력이면 결과 ISO는 바이트 단위로 동일합니다.

배포용 패치는 xdelta3으로 만듭니다.

```bash
xdelta3 -e -9 -B 1073741824 -s "Star Fox - Assault (Japan).iso" "Star Fox - Assault [KO].iso" release/StarFoxAssault_KO_v0.9.xdelta
```

## 원문 텍스트에 대해

`tools/text/*.json`에는 **번역문만** 들어 있습니다(항목 이름 + 한국어). 일본어·영어 원문은 게임 데이터라 저장소에 넣지 않았습니다.
번역 도구(`tm_apply.py`, `menu_apply.py`, `todo.py`)는 원문이 필요하므로, 직접 가진 ISO에서 다시 추출해 쓰세요.

```bash
python dump.py "../Star Fox - Assault (Japan).iso" /fpc/s_01_01.fpc jp_s0101.fpc
python dump.py "../Star Fox - Assault (USA).iso" /fpc/s_01_01.fpc us_s0101.fpc
python extract_text2.py jp_s0101.fpc us_s0101.fpc text/s01.json
```

## 구조

```
tools/
  build_all.py      전체 빌드 (스토리 → 메뉴 → 텍스처 → ISO 재구성·검증)
  kolib.py          SELT 인코딩, 장면별 한글 글리프 아틀라스(I4), 파일 현지화, ISO 재구성/검증
  build_menu.py     메뉴: ROM 폰트 대체 + 메뉴 SELT + rel/DOL 문자열 + 이름 입력 글자표
  kofont.py         한글 SJIS 폰트(Yay0) 생성, DOL 패치(폰트 섹션·OSReadROM 스텁·ArenaLo)
  build_tex.py      텍스처 한글화 적용 (크기+내용 해시로 모든 사본 교체)
  texspec.py        텍스처 편집 사양 1 (texcands.json 후보 번호 기준)
  texspec2.py       텍스처 편집 사양 2 (전수 스캔 scanA~D.json 참조)
  texedit.py        글자 지우기/쓰기, 아이콘 라벨 정렬, CMPR·C4·C8 인코더
  gcfs.py fpctree.py selt3.py nut.py gxtex.py gcfont.py yay0.py dol.py   포맷 라이브러리
  extract_*.py tm_apply.py apply_ko.py menu_apply.py todo.py              텍스트 추출·번역 적용
  punct.py sync_ko.py                                                    문장부호 검수·번역 원고 동기화
  texdiff.py texcands.py texscan*.py texview.py texpreview.py iconscan.py 텍스처 조사 도구
  alltex.json texcands.json texdiff.json texmissing.json scan?.json      텍스처 목록(오프셋·해시)
  text/
    *.json          번역문 (항목 이름 + 한국어)
    sNN_ko.py b_ko.py menu_ko.py   번역 원고
  _work/            (git 제외) 원문 포함 텍스트·덤프·미리보기 이미지·폐기 스크립트
release/            배포용 xdelta 패치 + 사용 설명서
```

## 번역 수정 흐름

- 스토리: `text/sNN_ko.py`(또는 `b_ko.py`) 수정 → `python tm_apply.py text/sNN.json text/sNN_ko.py` → 빌드.
  빌드는 `text/*.json`의 `ko` 값을 사용하므로 두 곳이 같게 유지돼야 합니다.
- 메뉴: `text/menu_ko.py` 수정 → `python menu_apply.py` → 빌드.
- 줄 폭 초과(무전 408px / 데모 504px)나 한자·가나 혼입이 있으면 빌드가 멈춥니다.

## 표기 원칙

- 이름: 폭스, 팔코, 슬리피, 페피, 크리스탈, 나우스(ROB), 페퍼 장군, 벨티노, 안드로스, 오이코니, 피그마, 울프, 팬서, 레온, 트리키
- 용어: 라일라트, 콜로니, 팩토리, 아윙, 랜드마스터, 아파로이드, 마더
- 말투: 페퍼 장군=하게체, 나우스=딱딱한 존댓말, 피그마=경상도 사투리, 울프=거친 반말, 팬서=느끼함, 레온=음흉, 트리키=어린아이

## 기술 메모

- 컨테이너: `.fpc/.pac` = `[개수, 오프셋…, 끝]` 재귀 컨테이너 + NPAC(`'NPAC'`, 전체, 데이터 크기, 인덱스).
- 텍스트: SELT(`'SELT'`, 항목 수, 언어 수 2). 32bit 코드, `0`=끝, `FFFFFFFF`=줄바꿈, `A000:n`=화자, `6018/6030:n`=버튼 아이콘.
  스토리는 `0x20|폭<<16|글리프번호`로 앞 NPAC의 I4 아틀라스(1024폭, 24×24칸, 줄당 42)를 참조 → 한글 아틀라스를 새로 생성.
- 메뉴는 본체 IPL ROM의 SJIS 폰트(24×24, 2bpp)를 씀 → 한글 음절을 JIS 1수준 한자 코드(0x889F~)에 배치한 폰트를 DOL 새 섹션(0x803A1D00)에 넣고
  `__OSReadROM` 호출(0x80130088)을 복사 스텁으로 교체. ArenaLo 상수 2곳 + `OSSetArenaLo` 클램프로 힙이 폰트를 덮지 않게 함.
  이름 입력 음절은 코드가 바뀌지 않도록 폰트 배치 맨 앞에 고정(메모리카드 이름 호환).
- 이름 입력 글자표: `m2.rel` 0x18040 / 0x180B8 (각 59칸, 5줄×12칸).
- 텍스처: NUTC(fmt4=CMPR, 5=C4, 6=C8 — 이 게임의 C8은 8×4 블록, 3=RGBA8). GIDX는 재사용되므로 (폭, 높이, 내용 MD5)로 식별.
