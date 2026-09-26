# 스타폭스 어설트 (GC) 한글 패치

*Star Fox: Assault* (게임큐브, 일본판 `GF7J01`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v1.1](../../releases/tag/v1.1)**

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

- 일본판 ISO. 북미·유럽판에는 적용할 수 없습니다. RVZ·GCM으로 갖고 있다면 Dolphin으로 ISO로 바꾼 뒤 적용하세요.
- xdelta 패치 도구. [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher)(GUI)나 [xdelta3](https://github.com/jmacd/xdelta-gpl/releases)(명령줄)를 쓰면 됩니다.

### 적용 방법

1. [배포 페이지](../../releases/latest)에서 `StarFoxAssault_KO_v1.1.xdelta`를 받습니다.
2. 일본판 원본 ISO에 패치를 적용합니다. 기존 한글판 ISO에 덧씌우는 패치가 아닙니다. xdelta3에서는 다음처럼 실행합니다.

   ```
   xdelta3 -d -s "Star Fox - Assault (Japan).iso" StarFoxAssault_KO_v1.1.xdelta "Star Fox - Assault (Korean).iso"
   ```

3. 결과 파일의 확인값을 아래 표와 비교합니다.

자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 파일 확인값

| 항목 | 원본 일본판 | 패치 적용 결과 (v1.1) |
|---|---|---|
| 크기 | 1,459,978,240 바이트 | 1,459,978,240 바이트 |
| CRC32 | `089208F3` | `AADAC46F` |
| MD5 | `27aed37f24061b1ff06cdd3640053481` | `68556a9dcec0fe9aaad9d8b669038891` |
| SHA-1 | `43327ab2772003d0e5122c5b321153b1436131d3` | `fd15e4515f8ef2232cc2735c5189c8a16e4985d0` |
| SHA-256 | `d929247af95ee17479912291bc66b8c71d22785f9576ea7b8eff9c95947cccba` | `2a5f13dd7beb30eaea81a6f2862ecfa0886397e1a213bf4ceac2502c31b32269` |

원본 파일명 예: `Star Fox - Assault (Japan).iso`

### 실행 환경

- **확인함**: Dolphin, Wii U vWii + Nintendont, Wii U VC 주입(UWUVCI).

### 알려진 문제

- 스테이지 배경의 간판·전광판, 배틀 모드의 결과 표시(COMPLETE, GAME OVER 등),
  무기 이름, 배지 문구는 일본판 원본부터 영문 디자인이라 그대로 두었습니다.
- 게임 안 이미지 3,737개를 전수 확인했습니다. 화면에 나오는 것 중 일본어가 남은 것은 없습니다.
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
- xdelta3. 배포용 패치를 만들 때만 필요하며, PATH에 두거나 환경 변수 `XDELTA3`로 지정합니다.

### 빌드

```bash
# 한글 ISO 만들기 (work/StarFoxAssault_KO.iso)
python tools/build.py

# 배포용 패치까지: 빌드, xdelta 패치 생성, 적용 결과 해시 검증
python tools/make_patch.py 1.1
```

일본판 ISO를 읽어 변경 파일 58개와 패치된 DOL로 이미지를 다시 구성하고, 파일 1090개를 모두 원본과 비교해 검증합니다.
같은 입력이면 결과는 바이트 단위로 같습니다. Windows Git Bash에서는 `MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8`을 붙이세요.

### 번역 수정

- 대사: [`translation/drafts/*_ko.py`](translation/drafts)를 고친 뒤 `python tools/tm_apply.py translation/ko/sNN.json translation/drafts/sNN_ko.py`를 실행하고 빌드합니다.
- 메뉴: [`translation/drafts/menu_ko.py`](translation/drafts/menu_ko.py)를 고친 뒤 `python tools/menu_apply.py`를 실행하고 빌드합니다.
- 그림 글씨: [`tools/texspec.py`](tools/texspec.py)와 [`tools/texspec2.py`](tools/texspec2.py)를 고친 뒤 빌드합니다.
- 타이틀: 일본판 영문 로고를 유지하고 일본어 부제만 한글화합니다. [`tools/build_logo.py`](tools/build_logo.py)와 `tools/assets/title_subtitle_ko.png`를 쓰며, 북미판 ISO는 필요 없습니다.
- 표기·말투·문장부호 원칙은 [`translation/GLOSSARY.md`](translation/GLOSSARY.md), 검수 기준은 [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md)를 참고하세요.
- 직역투 후보 찾기: `python tools/jpcheck.py`.
- 검사: `python tools/check_ko.py`(빈 줄, 한자·가나 혼입, 줄 폭, 줄 수). 여러 파일에 복사된 대사는 `python tools/sync_dup.py --apply`로 맞춥니다.
- 빌드는 `translation/ko/*.json`의 `ko` 값을 씁니다. 줄 폭 초과(무전 408px, 데모 504px)나 한자·가나 혼입이 있으면 멈춥니다.

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
release/           배포용 xdelta 패치와 사용자 설명서
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
