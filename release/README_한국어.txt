스타폭스 어썰트 한글패치 v0.91 (게임큐브 / 일본판 기준)
=========================================================

■ 준비물
  - 일본판 ISO   Star Fox - Assault (Japan).iso
      CRC32 089208F3 / MD5 27aed37f24061b1ff06cdd3640053481
      (RVZ·GCM 등으로 갖고 계시면 Dolphin으로 ISO 변환 후 사용)
  - 패치 파일     StarFoxAssault_KO_v0.91.xdelta
  - 패치 도구     xdelta3 또는 Delta Patcher 같은 GUI 도구

■ 적용 방법
  1) Delta Patcher (GUI)
     - Original file: 일본판 ISO
     - XDelta patch:  StarFoxAssault_KO_v0.91.xdelta
     - Apply patch 클릭

  2) xdelta3 (명령줄)
     xdelta3 -d -s "Star Fox - Assault (Japan).iso" StarFoxAssault_KO_v0.91.xdelta "Star Fox - Assault (Korean).iso"

■ 결과 파일 확인 (여기와 다르면 원본 ISO가 다른 것입니다)
  CRC32 8E03EC77
  MD5   d91e97fe2f90aad0a7cb97e64e9491a2
  SHA1  a6f3d307b498603c64b164f1277ece660aeac8ec
  크기  1,459,978,240 바이트

■ 한글화 범위
  - 스토리: 미션 1~10 무전·데모 대사, 무비 자막, 브리핑
  - 메뉴: 싱글·배틀·옵션·결과·메모리카드 메시지
  - 그래픽: 미션 부제, 행성 이름, 메뉴 라벨, 타이틀 로고 등
  - 이름 입력 화면을 한글 음절표로 교체

■ 확인 환경
  - Dolphin 에뮬레이터에서 동작 확인 (실기는 미확인)

■ v0.91 변경 내용
  - 글자 주변에 지저분하게 보이던 픽셀 정리 (대사창, 메뉴 버튼, 결과 화면)
  - 대사 문장부호 검수: 화자가 바뀌는 자리에 마침표, 부르는 말 뒤 쉼표
  - 일본어 직역투 정리 (약 320줄)
  - 인물·지명을 정식 발매판 표기로 통일 (안돌프, 카티나, 코네리아, 그레이트폭스 등)
  - 메모리 카드 확인창의 예 / 아니요 한글화
  - 조작 설정 화면 글자 위치 정리

■ 알려진 사항
  - 실기(게임큐브·Wii)에서는 확인하지 않았습니다.
  - 배틀 모드 일부 화면과 스테이지 배경의 글자 이미지는 아직 일본어로 남아 있을 수 있습니다.
  - 잘못된 번역이나 깨진 글자를 발견하면 제보해 주세요.

■ 제보·문의
  https://github.com/arqhive/star-fox-assault-korean-translation/issues

※ 이 패치에는 게임 데이터가 들어 있지 않습니다. 정품 ISO가 있어야 사용할 수 있습니다.
