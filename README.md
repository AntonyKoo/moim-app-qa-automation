# MOIM App QA Automation

MOIM 앱의 자동화 테스트 프로젝트입니다.

## 프로젝트 구조

```
moim-app-qa-automation/
├── config/                 # 설정 파일 디렉토리
│   ├── devices.json       # 디바이스 설정
│   └── test_data.json     # 테스트 데이터
├── tests/                 # 테스트 코드 디렉토리
│   └── android/          # Android 테스트
│       ├── connection_test.py
│       └── tc1_launch_and_login.py
├── utils/                 # 유틸리티 함수 디렉토리
├── reports/              # 테스트 리포트 디렉토리
├── venv/                 # Python 가상환경
├── .env                  # 환경 변수 파일 (git에 포함되지 않음)
├── .gitignore           # Git 제외 파일 목록
└── requirements.txt      # Python 패키지 의존성
```

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/AntonyKoo/moim-app-qa-automation.git
cd moim-app-qa-automation
```

2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 환경 변수들을 설정합니다:
```
APPIUM_PLATFORM_NAME=
APPIUM_AUTOMATION_NAME=
APPIUM_DEVICE_NAME=
APPIUM_UDID=
APPIUM_APP_PACKAGE=
APPIUM_APP_ACTIVITY=
APPIUM_NO_RESET=
APPIUM_SERVER_URL=
```

## 실행 방법

1. Appium 서버 실행
```bash
appium
```

2. 테스트 실행
```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 파일 실행
pytest tests/android/tc1_launch_and_login.py
```

## 주요 의존성 패키지

- Appium-Python-Client 2.9.0: Appium 자동화 프레임워크
- pytest 7.3.1: 테스트 실행 프레임워크
- pytest-html 3.2.0: HTML 리포트 생성
- python-dotenv: 환경 변수 관리
- google-api-python-client: Google API 클라이언트
- pillow: 이미지 처리

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 않습니다
- `venv` 디렉토리도 Git에 포함되지 않습니다
- 테스트 실행 전 Appium 서버가 실행 중이어야 합니다

## 테스트 구조

- `tests/android/`: Android 플랫폼 테스트
  - `connection_test.py`: 기본 연결 테스트
  - `tc1_launch_and_login.py`: 앱 실행 및 로그인 테스트 