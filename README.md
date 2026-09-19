# 스타폭스 어썰트 한글 패치

*Star Fox: Assault* (게임큐브, 일본판 `GF7J01`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive**

- 대사 전체 한글화 (미션 1~10 무전·데모 대사, 무비 자막, 미션 브리핑)
- 메뉴 전체 한글화 (싱글·배틀·옵션·결과·메모리카드 메시지)
- 본체 IPL ROM 의 SJIS 폰트를 한글 폰트로 교체하고 DOL 을 패치
- 그림 글씨 96종 한글화 (미션 부제, 행성 이름, 버튼 라벨, 무전 화자 이름표, 타이틀 로고)
- 이름 입력 화면을 한글 음절표로 교체 (메모리카드에 저장한 이름도 유지)
- **원본과 같은 1.4GB 디스크 크기 유지**
- 확인 환경: Dolphin 에서 스토리·대전·보너스 게임·메뉴 전부 검수 / **실기는 확인하지 않았습니다**

> 이 저장소에는 **게임 데이터(ISO, 추출한 원문 대사, 그래픽)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

[릴리스 페이지](../../releases)에서 `.xdelta` 패치를 받아 일본판 ISO 에 적용하세요.
자세한 방법은 [`release/README_한국어.txt`](release/README_한국어.txt)에 있습니다.

| 원본 (일본판) | 값 |
|---|---|
| 파일명 예 | `Star Fox - Assault (Japan).iso` |
| 크기 | 1,459,978,240 바이트 |
| CRC32 | `089208F3` |
| MD5 | `27aed37f24061b1ff06cdd3640053481` |

| 패치 적용 결과 (v1.0) | 값 |
|---|---|
| 크기 | 1,459,978,240 바이트 (원본과 같음) |
| CRC32 | `A4C839CB` |
| MD5 | `597c5125c7ca44f80da1ddd914d0a85a` |
| SHA1 | `324e03041506af7a9e2ad4c84f425fcdd519d38d` |

- 북미·유럽판에는 적용할 수 없습니다. RVZ·GCM 으로 갖고 계시면 Dolphin 으로 ISO 로 바꾼 뒤 적용하세요.
- 패치 도구: [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher)(GUI) 또는 [xdelta3](https://github.com/jmacd/xdelta-gpl/releases)(명령줄).

### 알려진 문제

- 실기(Wii·게임큐브)에서는 확인하지 않았습니다.
- 스테이지 배경에 그려진 글자(간판 등)는 원본 그대로 일본어입니다.
- 이름 입력은 준비된 음절표(120자) 안에서만 쓸 수 있습니다.
- 설명 상자의 한 줄짜리 문구는 원래 두 줄 기준 배치라 살짝 아래에 놓입니다.
- 무전 화자 이름표는 256색 팔레트 제약으로 글자 가장자리가 다소 거칠게 보입니다.
- 보너스 게임(제비우스 등)을 돌핀에서 돌릴 때는 **그래픽 설정 → 향상 → 텍스처 필터링을 `기본값`으로** 두세요. 니어리스트·리니어로 강제하면 화면이 깨집니다.

## 개발자용: 직접 빌드

### 요구 사항

| 항목 | 비고 |
|---|---|
| Python 3.11 이상 | `pip install -r requirements.txt` (numpy, Pillow, opencv-python) |
| 일본판 ISO | 저장소 루트나 `iso/` 에 두거나 환경 변수 `SFA_JP_ISO` 로 지정 |
| 북미판 ISO | 타이틀 로고를 가져오는 데만 필요 — `SFA_US_ISO` |
| `font_japanese.bin` | Dolphin 의 `Sys/GC/` 에 있는 파일. 경로가 다르면 `GC_FONT_JAPANESE` |
| 맑은 고딕 Bold | `C:/Windows/Fonts/malgunbd.ttf` — 한글 글리프를 그리는 데 사용 |
| xdelta3 | 배포용 패치를 만들 때만 필요 — PATH 또는 `XDELTA3` |

### 빌드

```bash
# 한글 ISO 만들기 (work/StarFoxAssault_KO.iso)
python tools/build.py

# 배포용 패치까지: 빌드 → xdelta 패치 → 적용해서 해시 검증
python tools/make_patch.py 1.0
```

일본판 ISO 를 읽어 변경 파일 58개와 패치된 DOL 로 이미지를 다시 구성하고, 파일 1090개를 전부 원본과 비교해 검증합니다.
같은 입력이면 결과는 바이트 단위로 같습니다. Windows Git Bash 에서는 `MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8` 을 붙이세요.

### 번역 수정

- 대사: [`translation/drafts/*_ko.py`](translation/drafts) 수정 → `python tools/tm_apply.py translation/ko/sNN.json translation/drafts/sNN_ko.py` → 빌드
- 메뉴: [`translation/drafts/menu_ko.py`](translation/drafts/menu_ko.py) 수정 → `python tools/menu_apply.py` → 빌드
- 그림 글씨: [`tools/texspec.py`](tools/texspec.py), [`tools/texspec2.py`](tools/texspec2.py) 수정 → 빌드
- 표기·말투·문장부호 원칙은 [`translation/GLOSSARY.md`](translation/GLOSSARY.md), 검수 기준은 [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md) 참고
- 직역투 후보 찾기: `python tools/jpcheck.py`
- 검사: `python tools/check_ko.py` (빈 줄·한자/가나 혼입·줄 폭·줄 수), 여러 파일에 복사된 대사 맞추기: `python tools/sync_dup.py --apply`
- 빌드는 `translation/ko/*.json` 의 `ko` 값을 씁니다. 줄 폭 초과(무전 408px / 데모 504px)나 한자·가나 혼입이 있으면 멈춥니다.

`translation/ko/*.json` 에는 **번역문만** 들어 있습니다(항목 이름 + 한국어).
일본어·영어 원문은 게임 데이터라 넣지 않았으므로, 원문이 필요한 도구(`tm_apply.py`, `menu_apply.py`, `todo.py`)를 쓰려면 직접 가진 ISO 에서 다시 추출하세요.

```bash
python tools/dump.py "<일본판 ISO>" /fpc/s_01_01.fpc work/jp_s0101.fpc
python tools/dump.py "<북미판 ISO>" /fpc/s_01_01.fpc work/us_s0101.fpc
python tools/extract_text2.py work/jp_s0101.fpc work/us_s0101.fpc translation/ko/s01.json
```

## 구조

```
tools/          빌드·패치·조사 도구 (paths.py 가 기준 경로를 잡음)
  data/         텍스처 목록(오프셋·해시)
translation/
  ko/           번역 JSON (항목 이름 + 한국어)
  drafts/       번역 원고 (.py)
  GLOSSARY.md   표기·말투·문장부호 원칙
docs/
  TECHNICAL.md  파일 포맷과 한글화 방식
  REVIEW_GUIDE.md  대사 검수 기준(마침표·쉼표·직역투)
release/        배포용 xdelta 패치 + 사용 설명서
work/           (git 제외) 빌드 결과·원문·미리보기
```

## 라이선스

도구와 번역 텍스트는 [MIT 라이선스](LICENSE)를 따릅니다.
게임 데이터의 권리는 Nintendo / NAMCO 에 있으며, 이 저장소와 패치에는 게임 데이터가 들어 있지 않습니다.
