스타폭스 어썰트 한글패치 v1.0 (게임큐브 / 일본판 기준)
======================================================

■ 준비물
  - 일본판 ISO   Star Fox - Assault (Japan).iso
      CRC32 089208F3 / MD5 27aed37f24061b1ff06cdd3640053481
      (RVZ·GCM 등으로 갖고 계시면 Dolphin으로 ISO 변환 후 사용)
  - 패치 파일     StarFoxAssault_KO_v1.0.xdelta
  - 패치 도구     xdelta3 또는 Delta Patcher 같은 GUI 도구

■ 적용 방법
  1) Delta Patcher (GUI)
     - Original file: 일본판 ISO
     - XDelta patch:  StarFoxAssault_KO_v1.0.xdelta
     - Apply patch 클릭

  2) xdelta3 (명령줄)
     xdelta3 -d -s "Star Fox - Assault (Japan).iso" StarFoxAssault_KO_v1.0.xdelta "Star Fox - Assault (Korean).iso"

■ 결과 파일 확인 (여기와 다르면 원본 ISO가 다른 것입니다)
  CRC32 A4C839CB
  MD5   597c5125c7ca44f80da1ddd914d0a85a
  SHA1  324e03041506af7a9e2ad4c84f425fcdd519d38d
  크기  1,459,978,240 바이트

■ 한글화 범위
  - 스토리: 미션 1~10 무전·데모 대사, 무비 자막, 브리핑
  - 메뉴: 싱글·배틀·옵션·결과·메모리카드 메시지
  - 그래픽: 미션 부제, 행성 이름, 메뉴 라벨, 타이틀 로고 등
  - 이름 입력 화면을 한글 음절표로 교체

■ 확인 환경
  - Dolphin 에뮬레이터에서 스토리·대전·보너스 게임·메뉴 전부 검수
  - 실기(게임큐브·Wii)는 미확인

■ v1.0 변경 내용
  - 대전(배틀) 모드와 보너스 게임까지 전 모드 검수 완료
  - 배틀 핸디캡 설정값 한글화 (작게 / 크게)
  - 배틀 룰 설정 화면: 항목 정렬과 글자 주변 얼룩 정리
  - 룰 설명 띠의 글자가 왼쪽 아이콘을 덮던 문제 수정
  - 종료 메뉴 / 일시정지 메뉴의 글자 크기 통일
  - 보너스 게임 조작 설명에서 글자가 상자 밖으로 나가던 문제 수정
  - 무전 화자 이름표 가독성 개선 (받침 ㄹ 이 뭉개지던 문제)
  - 용어 정리: 리스타트 → 재시작, 셀렉트 → 선택
  - 일본어 직역투 추가 정리

■ 알려진 사항
  - 실기(게임큐브·Wii)에서는 확인하지 않았습니다.
  - 스테이지 배경에 그려진 글자(간판 등)는 원본 그대로 일본어입니다.
  - 보너스 게임(제비우스 등)을 돌핀에서 돌릴 때는 그래픽 설정 →
    향상 → 텍스처 필터링을 '기본값' 으로 두세요.
    니어리스트·리니어로 강제하면 화면이 깨집니다.
  - 잘못된 번역이나 깨진 글자를 발견하면 제보해 주세요.

■ 제보·문의
  https://github.com/arqhive/star-fox-assault-korean-translation/issues

※ 이 패치에는 게임 데이터가 들어 있지 않습니다. 정품 ISO가 있어야 사용할 수 있습니다.
