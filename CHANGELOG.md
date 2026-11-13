# 변경 기록

## 0.2

- Windows 기본 런처에서 Android 설정 화면 열기
- 무선 ADB 페어링 및 연결, mDNS 검색과 기기 시리얼 확인
- 미디어·방해 금지·시스템 효과음 설정 및 검증
- 두 APK의 SHA-256 검증, 설치 확인, 콘솔 실행 및 진행 로그 저장

## 0.1

- Windows 대화형 런처와 Python CLI 추가
- Preloader 모드 요청 및 부트로더 Fastboot·Fastbootd 상태 조회
- USB 드라이버 서비스 확인
- 기존 순정 덤프 검증, 백업 사본 저장, SHA-256 매니페스트 생성

- 실기기 LineageOS 초기 설정 화면 진입 확인을 검증 기록에 반영. ADB·하드웨어 진단은 미확인.

## 0.3
- 백업·언락·선택적 OS 설치 순차 실행 GUI 추가.
- 전체 GPT 엔트리 재읽기 및 CRC 검증, seccfg 첫 섹터 쓰기 제한.
- 실제 커넥트에서 통합 Android 음소거·두 앱 설치·실행 검증 통과.
- 백업부터 OS까지 통합 실기기 재검증과 자동 복원은 미완료.

## 0.4
- 설정 검사·준비 상태 탭, 누락 설정별 조치, 실행 전 차단 추가.
- ADB 인증/연결/APK 오류 분류 및 입력·중복 실행 잠금.
- 완료·실패 단계 체크포인트 저장.

## 미리보기 디자인
- 설치 마법사 형태: 작업 선택, 연결, 준비 확인, 진행, 완료.
- Preview.cmd는 installer_preview.py를 실행하며 외부 명령을 차단.
- 정상 흐름 4종, 오류 복귀, 화면 배치를 확인.

## 0.5 preparation
- Korean, English and Japanese language selection in both GUIs.
- Source-only export, GPL-3.0 notices, translated documentation and offline CI.
- No GitHub publication or additional hardware writes performed.

## 0.5-rc2 source preparation
- Separate repositories for OS tooling, diagnostics, and console.
- Remove bundled development APK hashes and automatic private-workspace APK selection.
- Audit all allowlisted/unreviewed source files, Git index, and ZIP contents before release.
- No new device operations or GitHub publication during packaging.
