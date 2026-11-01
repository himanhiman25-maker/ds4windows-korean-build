# DS4Windows 4.6.7 한국어 확장 빌드

hbashton/DS4Windows `VIIPERRC4.6.7`의 표시 문구를 한국어로 확장하는 비공식 소스 오버레이입니다.
현재 검증한 빌드는 **VIIPERRC4.6.7-ko.3**입니다.

## 검증 결과

- [ko.3 성공한 빌드](https://github.com/himanhiman25-maker/ds4windows-korean-build/actions/runs/41284748085)
- 자동 검사: **7,202개 통과, 실패 0개, 12개 건너뜀**.
- 한국어 리소스: **1,676개**, `ko`와 `ko-KR`에서 검사 통과.
- ko.2의 1,314개에서 리소스 362개를 추가했습니다.
- 화면 속성 965곳의 번역 연결 외에 C#에서 만드는 표시 문구를 추가로 연결했습니다.
- 배포용 `Lang/ko` 폴더에서 실제 리소스 로딩 검사 통과.
- 빌드한 오버레이 커밋: `ea79b9c67cdb4ac9f688e3037195c87456114fc3`.
- 실제 Windows 설치에서 설정, 버튼 매핑, 특수 동작, 라이트바, 오디오 햅틱,
  트리거 연구소·프리셋, Nintendo 조준, 고급 오디오·마이크, 로그 화면의 한국어 표시를 확인했습니다.
- 실제 물리 컨트롤러·게임 입력은 별도 검증이 필요합니다.

## ko.3에서 추가한 범위

- 트레이의 시작·중지, 열기, 최소화, 프로그램 폴더 열기, 종료와 연결 해제 메뉴.
- Bluetooth 검색, 장치 등록·재연결, Joy-Con 결합과 개수 안내, VIIPER 준비 상태.
- 버튼·스틱·마우스 매핑의 표시 이름과 기본 특수 동작 이름.
- 최대 밝기와 컨트롤러 선택 안내.
- 오디오 소스, 혼합·대체 설명과 실행 상태.
- 트리거 연구소 내부 컨트롤, 프리셋 이름·설명, 최대 입력 동작, 게임 진동, 미리보기와 초기화.
- Nintendo 기울기 조준과 가상 출력·PlayStation 스피커·마이크 설명.
- 화면 로그의 기본 진단 문구와 프로필 편집 시간.

화면 표시를 번역하며 프로필에 저장되는 식별자·값과 사용자 지정 이름은 유지합니다.
파일 로그는 원문을 보존합니다. 외부 프로그램의 오류 원문, 제품명·장치 식별자와 사용자 작성 내용은 영어로 표시될 수 있습니다.
장치 종류·연결 상태에 따른 모든 실제 하드웨어 조합의 검증을 뜻하지는 않습니다.

## 빌드

1. **Actions → Build DS4Windows 4.6.7 Korean → Run workflow**에서 `main`을 선택합니다.
2. 성공한 실행의 **Artifacts → DS4Windows-4.6.7-Korean-x64**를 받습니다.
3. 그 안의 `DS4Windows_VIIPERRC4.6.7-ko.3_x64.zip`이 실행용 ZIP입니다.

표준 공개 `windows-2022` 서버를 사용합니다. 사용자 PC에 .NET SDK나 Visual Studio를 설치하지 않습니다.
비공개 저장소에서는 실행을 건너뛰도록 제한했습니다. 공개 저장소의 표준 서버 컴퓨팅은
[GitHub 공식 정책](https://docs.github.com/en/billing/concepts/product-billing/github-actions)에 따라 무료입니다.
결과는 1일 후 만료되므로 다운로드해 보관하세요.
`main`의 일반 변경은 빌드를 시작하지 않습니다. `feature/complete-korean-ui` 분기만 변경 시 자동 검증합니다.

## 적용 주의

현재 앱과 실제 사용자 설정을 백업하고 종료한 뒤 적용하세요.
ZIP은 포터블 구성입니다. 기존 `Program Files` 관리 설치에는 루트의 `DS4Windows.portable`,
`viiper.exe`, `viiper.exe.sha256`을 복사하지 않고 소유 파일 목록에서도 제외해야 합니다.
기존 설치형 `VIIPER/viiper.exe`는 번역을 위해 교체할 필요가 없습니다.
이전 루트 `ko/DS4Windows.resources.dll`은 새 `Lang/ko` 번역을 가릴 수 있으므로 백업 후 분리하세요.
언어 선택 후에는 앱을 재시작합니다. 공식 앱 업데이트로 본체 번역이 덮어써질 수 있습니다.

## 소스와 라이선스

- 고정 원본: [hbashton/DS4Windows](https://github.com/hbashton/DS4Windows/tree/080495de61ae8b6ada6b4252337838e8b22119b8)
- `apply_korean.py`, `support/apply_dynamic.py`: 표시 문구 연결과 언어 저장 수정.
- `data/ui-ko.json`, `data/dynamic-ko.tsv`, 한국어 `.resx`: 번역 자료.
- `validate_korean.py`: 구조·바인딩·서식 인수와 표시 외 코드의 보존 확인.
- `support/`: 표시 변환, 리소스·사용자 지정 이름 보존 검사와 기존 레이아웃 검사 보조 소스.

개인 프로필·설정·백업·로그·인증 정보는 저장소에 포함하지 않습니다.
수정본은 이 저장소의 오버레이와 고정 원본으로 재생성할 수 있습니다.
원본 프로젝트와 이에 기반한 수정은 GPL-3.0 조건을 따릅니다. `LICENSE.txt`를 참고하세요.
