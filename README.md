# 스타폭스 어설트 (GC) 한글 패치

*Star Fox: Assault* (게임큐브, 일본판 `GF7J01`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v1.2f](../../releases/tag/v1.2f) (최종판)**

- 대사 전체를 한글화했습니다(미션 1에서 10까지의 무전·데모 대사, 무비 자막, 미션 브리핑).
- 메뉴 전체를 한글화했습니다(싱글·배틀·옵션·결과·메모리카드 메시지).
- 본체 IPL ROM의 SJIS 폰트를 한글 폰트로 바꾸고 DOL을 패치했습니다. 부팅 때 나오는 시스템 메시지도 한글화했습니다.
- 그림 글씨 96종(미션 부제, 행성 이름, 버튼 라벨, 무전 화자 이름표)과 타이틀 로고 부제를 한글화했습니다.
- 이름 입력 화면을 한글 음절표로 바꿨습니다. 메모리카드에 저장한 이름도 그대로 유지됩니다.
- **원본과 같은 1.4GB 디스크 크기를 유지합니다.**

> 이 저장소에는 **게임 데이터(롬·디스크 이미지, 추출한 원문 대사, 그래픽, 스크린샷)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 일본판(`GF7J01`) 이미지. ISO·GCM은 그대로, CISO·WIA·WDF·GCZ는 패처가 ISO로 바꿔서 적용합니다.
- Windows 10 이상(기본 PowerShell 사용). 다른 도구는 필요 없습니다.

| 원본 형식 | 결과 | 비고 |
|---|---|---|
| ISO, GCM | ISO | |
| CISO, WIA, WDF, GCZ | ISO | 동봉한 wit으로 ISO로 바꾼 뒤 적용 |
| RVZ | 지원 안 함 | Dolphin에서 ISO로 변환한 뒤 적용 |
| NKit | 지원 안 함 | NKit 도구로 원래 ISO로 되돌린 뒤 적용 |

패처가 게임 파일 하나하나를 원본과 비교하므로, 덤프 방식에 따라 ISO 전체 MD5가 달라도 게임 파일만 같으면 적용됩니다. 북미판·유럽판과 이미 한글 패치를 적용한 이미지에는 적용되지 않습니다.

### 적용 방법

1. [배포 페이지](../../releases/tag/v1.2f)에서 `GF7J_KPatch_v1.2f.zip`을 받아 풉니다.
2. 풀린 폴더에 원본 이미지를 넣고 `패치하기.bat`을 더블클릭합니다. 원본 파일을 `패치하기.bat` 위에 끌어다 놓아도 됩니다.
3. 원본과 같은 폴더에 `Star Fox Assault (Korean).iso`가 생깁니다. 원본 파일은 그대로 남습니다.

결과 파일 이름을 바꾸려면 두 번째 인자로 지정합니다. 오류 메시지와 자세한 방법은 ZIP에 들어 있는 `README.txt`를 참고하세요.

```bash
패치하기.bat "Star Fox - Assault (Japan).iso" "D:/Games/Star Fox Assault (Korean).iso"
```

항상 일본판 원본에 적용합니다. 이전 버전 한글판 ISO에 덧씌우는 패치가 아닙니다.

### 원본 확인값

Redump 정본 ISO의 값입니다. 다른 덤프도 게임 파일이 같으면 적용됩니다. 정본에 적용하면 패처가 마지막에 「정본(Redump) 원본 기준 결과와 일치합니다」를 출력합니다.

| 항목 | 원본 일본판 |
|---|---|
| 크기 | 1,459,978,240 바이트 |
| CRC32 | `089208F3` |
| MD5 | `27aed37f24061b1ff06cdd3640053481` |
| SHA-1 | `43327ab2772003d0e5122c5b321153b1436131d3` |

원본 파일명 예: `Star Fox - Assault (Japan).iso`

### 실행 환경

- **확인함**: Dolphin, Wii U vWii + Nintendont, Wii U VC 주입(UWUVCI).

### 알려진 문제

- 스테이지 배경의 간판·전광판, 배틀 모드의 결과 표시(COMPLETE, GAME OVER 등),
  무기 이름, 배지 문구는 일본판 원본부터 영문 디자인이라 그대로 두었습니다.
- 이름 입력은 준비된 음절표(120자) 안에서만 쓸 수 있습니다.
- 설명 상자의 한 줄짜리 문구는 원래 두 줄 기준 배치라 살짝 아래에 놓입니다.
- 무전 화자 이름표는 256색 팔레트 제약으로 글자 가장자리가 다소 거칠게 보입니다.
- 보너스 게임(제비우스 등)을 Dolphin에서 돌릴 때는 **그래픽 설정 → 향상 → 텍스처 필터링을 `기본값`으로** 두세요. 니어리스트·리니어로 강제하면 화면이 깨집니다.

## 개발자용: 직접 빌드

### 요구 사항

- Python 3.11 이상. `pip install -r requirements.txt`로 numpy, Pillow, opencv-python, capstone을 설치합니다.
- 일본판 ISO. 저장소 루트나 `iso/`에 두거나 환경 변수 `SFA_JP_ISO`로 지정합니다.
- Dolphin의 `Sys/GC/`에 있는 `font_japanese.bin`. 경로가 다르면 환경 변수 `GC_FONT_JAPANESE`로 지정합니다.
- 맑은 고딕 Bold(`C:/Windows/Fonts/malgunbd.ttf`). 한글 글리프를 그리는 데 씁니다.
- 배포용 패처를 만들 때만: xdelta3 3.1.0과 wit v3.05a(cygwin64판). 패처 ZIP에 함께 넣습니다. 릴리즈 ZIP의 `bin/`에 든 것을 그대로 써도 됩니다(`--wit` 폴더는 `bin/wit.exe`·DLL과 `gpl-2.0.txt`가 있는 구조). 새로 클론한 폴더에서 빌드·패처 생성 결과가 v1.2f 배포본과 같음을 확인했습니다.

### 빌드

```bash
# 한글 ISO 만들기 (work/StarFoxAssault_KO.iso)
python tools/build.py

# 배포용 파일 단위 패처 (release/StarFoxAssault-KO-v<버전>/ 과 .zip)
python tools/make_patcher.py --orig "Star Fox - Assault (Japan).iso" --build work/StarFoxAssault_KO.iso \
    --out release/StarFoxAssault-KO-v1.2f --version 1.2f \
    --wit <wit 폴더> --xdelta <xdelta3.exe> --readme patcher/README.txt
```

일본판 ISO를 읽어 변경 파일 58개와 패치된 DOL로 이미지를 다시 구성하고, 파일 1090개를 모두 원본과 비교해 검증합니다.
같은 입력이면 결과는 바이트 단위로 같습니다. 패처(`patcher/patch.ps1`)는 빌드와 같은 배치 규칙으로 디스크를 다시 채우므로, 정본에 적용한 결과가 빌드 ISO와 MD5까지 같습니다. `make_patcher.py`가 만들 때 이 배치가 빌드와 같은지 먼저 확인합니다. Windows Git Bash에서는 `MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8`을 붙이세요.

### 번역 수정

- 대사: [`translation/drafts/*_ko.py`](translation/drafts)를 고친 뒤 `python tools/apply_ko.py translation/ko/sNN.json translation/drafts/sNN_ko.py`를 실행하고 빌드합니다. 반대로 JSON을 고쳤다면 `python tools/sync_ko.py --apply`로 원고에 맞춥니다.
- 메뉴: [`translation/drafts/menu_ko.py`](translation/drafts/menu_ko.py)를 고친 뒤 `python tools/menu_apply.py`를 실행하고 빌드합니다.
- 그림 글씨: [`tools/texspec.py`](tools/texspec.py)와 [`tools/texspec2.py`](tools/texspec2.py)를 고친 뒤 빌드합니다.
- 타이틀: 일본판 영문 로고를 유지하고 일본어 부제만 한글화합니다. [`tools/build_logo.py`](tools/build_logo.py)와 `tools/assets/title_subtitle_ko.png`를 쓰며, 북미판 ISO는 필요 없습니다.
- 표기·말투·문장부호 원칙은 [`translation/GLOSSARY.md`](translation/GLOSSARY.md), 검수 기준은 [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md)를 참고하세요.
- 직역투 후보 찾기: `python tools/jpcheck.py`.
- 검사: `python tools/check_ko.py`(빈 줄, 한자·가나 혼입, 줄 폭, 줄 수, 줄 끝 문장부호). 여러 파일에 복사된 대사는 `python tools/sync_dup.py --apply`로 맞춥니다.
- 빌드는 `translation/ko/*.json`의 `ko` 값을 씁니다. 줄 폭 초과나 한자·가나 혼입이 있으면 멈춥니다. 줄 폭 한계는 창마다 다르며(무전 288px, 스테이지 종료 대화 528px, 데모·브리핑 576px) 일본판 원문이 실제로 쓴 폭을 잰 값입니다([`tools/limits.py`](tools/limits.py), 재측정은 `python tools/jpwidth.py`).

`translation/ko/*.json`에는 **번역문만** 들어 있습니다(항목 이름과 한국어).
일본어·영어 원문은 게임 데이터라 넣지 않았습니다. 원문이 필요한 도구(`tm_apply.py`, `menu_apply.py`, `todo.py`)를 쓰려면 직접 가진 ISO에서 다시 추출하세요.

```bash
python tools/dump.py "<일본판 ISO>" /fpc/s_01_01.fpc work/jp_s0101.fpc
python tools/dump.py "<북미판 ISO>" /fpc/s_01_01.fpc work/us_s0101.fpc
python tools/extract_text2.py work/jp_s0101.fpc work/us_s0101.fpc translation/ko/s01.json
```

### 폴더 구조

```
tools/             빌드·패치·조사 도구 (paths.py가 기준 경로를 잡음)
  data/            텍스처 목록(오프셋·해시)
  assets/          한글 타이틀 부제 이미지
translation/
  ko/              번역 JSON (항목 이름과 한국어)
  drafts/          번역 원고 (.py)
  GLOSSARY.md      표기·말투·문장부호 원칙
docs/
  TECHNICAL.md     파일 포맷과 한글화 방식
  REVIEW_GUIDE.md  대사 검수 기준(마침표·쉼표·직역투)
  releases/        릴리즈 노트 사본
patcher/           사용자용 패처(patch.ps1, 패치하기.bat)와 설명서 README.txt
release/           (git 제외) make_patcher.py 가 만드는 배포 폴더·ZIP
work/              (git 제외) 빌드 결과·원문·미리보기
```

### 기술 문서

파일 포맷과 한글화 방식은 [`docs/TECHNICAL.md`](docs/TECHNICAL.md)에 정리했습니다.

## 변경 내역

전체 내역은 [`CHANGELOG.md`](CHANGELOG.md)에 있습니다.

## 크레딧·라이선스

- 이 저장소의 도구 코드, 한국어 번역문, 문서: [MIT License](LICENSE) (© 2026 arqhive).

## 면책

비공식 팬 번역이며 Nintendo와 관련이 없습니다. 「스타폭스 어설트」 관련 상표·저작권은 Nintendo와 NAMCO에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
