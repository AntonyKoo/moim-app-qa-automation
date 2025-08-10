# MOIM App QA Automation

MOIM 앱의 자동화 테스트 프로젝트입니다. Android 및 iOS 플랫폼을 지원하며, OCR 기반 UI 요소 인식과 권한 테스트를 포함한 포괄적인 QA 자동화를 제공합니다.

## 🎯 프로젝트 목적

- **자동화된 테스트 실행**: MOIM 앱의 주요 기능에 대한 자동화 테스트 수행
- **OCR 기반 UI 테스트**: EasyOCR을 활용한 텍스트 인식 기반 테스트
- **권한 테스트 자동화**: 다양한 사용자 권한 레벨별 테스트 시나리오
- **크로스 플랫폼 지원**: Android 및 iOS 플랫폼 지원
- **테스트 결과 관리**: Google Sheets 연동을 통한 테스트 결과 자동 기록

## 🏗️ 프로젝트 구조

```
moim-app-qa-automation/
├── config/                     # 설정 파일 디렉토리
│   ├── devices.json           # 디바이스 설정 정보
│   └── test_data.json         # 테스트 데이터 (더미 값)
├── tests/                     # 테스트 코드 디렉토리
│   ├── android/              # Android 플랫폼 테스트
│   │   ├── connection_test.py
│   │   ├── tc1_launch_and_login.py
│   │   ├── tc2_permission_guest.py
│   │   ├── tc3_permission_normal_user.py
│   │   ├── tc4_permission_role_user.py
│   │   └── tc5_permission_admin.py
│   ├── common/               # 공통 테스트 모듈
│   │   └── tc2_permission_guest.py
│   └── ios/                  # iOS 플랫폼 테스트 (준비 중)
├── utils/                     # 유틸리티 함수 디렉토리
│   ├── coordinates.py         # 좌표 기반 UI 요소 접근
│   ├── easyocr_utils.py      # OCR 기반 텍스트 인식
│   ├── driver_setup.py       # Appium 드라이버 설정
│   ├── helpers.py            # Google Sheets 연동 등 헬퍼 함수
│   ├── scroll_range_picker.py # 스크롤 범위 선택 도구
│   └── rel_position.json     # 상대 좌표 데이터
├── scripts/                   # 스크립트 도구
│   └── coordinate_picker.py  # 좌표 선택 도구
├── reports/                   # 테스트 리포트 디렉토리
├── venv/                     # Python 가상환경
├── .gitignore                # Git 제외 파일 목록
├── requirements.txt           # Python 패키지 의존성
└── setup.py                  # 패키지 설치 설정
```

## 🚀 주요 기능

### 🔍 OCR 기반 UI 테스트
- **EasyOCR 통합**: 텍스트 기반 UI 요소 자동 인식
- **키워드 매칭**: 다양한 텍스트 변형에 대한 유연한 매칭
- **스크린샷 분석**: 실시간 화면 분석을 통한 테스트 검증

### 📱 크로스 플랫폼 지원
- **Android**: Appium을 통한 완전한 자동화 테스트
- **iOS**: iOS 플랫폼 지원 준비 중
- **공통 모듈**: 플랫폼 간 공유 가능한 테스트 로직

### 🔐 권한 테스트 자동화
- **게스트 사용자**: 기본 권한 및 제한 기능 테스트
- **일반 사용자**: 표준 권한 레벨 테스트
- **역할 사용자**: 특정 역할 기반 권한 테스트
- **관리자**: 최고 권한 레벨 테스트

### 📊 테스트 결과 관리
- **Google Sheets 연동**: 테스트 결과 자동 기록
- **HTML 리포트**: pytest-html을 통한 상세 리포트 생성
- **스크린샷 저장**: 실패 케이스에 대한 시각적 증거

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/AntonyKoo/moim-app-qa-automation.git
cd moim-app-qa-automation
```

### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 환경 변수들을 설정합니다:

```bash
# Appium 설정
APPIUM_PLATFORM_NAME=Android
APPIUM_AUTOMATION_NAME=UiAutomator2
APPIUM_DEVICE_NAME=Android Device
APPIUM_UDID=your_device_udid
APPIUM_APP_PACKAGE=com.moim.app
APPIUM_APP_ACTIVITY=com.moim.app.MainActivity
APPIUM_NO_RESET=false
APPIUM_SERVER_URL=http://localhost:4723

# Google Sheets 연동 (선택사항)
GOOGLE_SHEET_ID=your_google_sheet_id
```

## 🏃‍♂️ 실행 방법

### 1. Appium 서버 실행
```bash
appium
```

### 2. 테스트 실행

#### 전체 테스트 실행
```bash
# 전체 테스트 실행
pytest tests/

# HTML 리포트 생성
pytest --html=reports/report.html tests/
```

#### 특정 테스트 실행
```bash
# Android 연결 테스트
pytest tests/android/connection_test.py

# 앱 실행 및 로그인 테스트
pytest tests/android/tc1_launch_and_login.py

# 권한 테스트 (게스트)
pytest tests/android/tc2_permission_guest.py
```

#### 특정 플랫폼 테스트
```bash
# Android 테스트만 실행
pytest tests/android/

# iOS 테스트만 실행 (준비 중)
pytest tests/ios/
```

## 🧪 테스트 시나리오

### 1. 기본 연결 테스트 (`connection_test.py`)
- Appium 서버 연결 확인
- 디바이스 연결 상태 확인
- 앱 설치 상태 확인

### 2. 앱 실행 및 로그인 테스트 (`tc1_launch_and_login.py`)
- 앱 실행 확인
- 알림 권한 팝업 처리
- 로그인 버튼 동작 확인

### 3. 권한 테스트 시리즈
- **게스트 권한** (`tc2_permission_guest.py`): 기본 권한 및 제한 기능
- **일반 사용자 권한** (`tc3_permission_normal_user.py`): 표준 권한 레벨
- **역할 사용자 권한** (`tc4_permission_role_user.py`): 특정 역할 기반 권한
- **관리자 권한** (`tc5_permission_admin.py`): 최고 권한 레벨

## 🛠️ 주요 의존성 패키지

| 패키지 | 버전 | 용도 |
|--------|------|------|
| Appium-Python-Client | 2.9.0 | Appium 자동화 프레임워크 |
| selenium | 4.9.1 | 웹 요소 상호작용 |
| pytest | 7.3.1 | 테스트 실행 프레임워크 |
| pytest-html | 3.2.0 | HTML 리포트 생성 |
| google-api-python-client | 2.86.0 | Google API 클라이언트 |
| pillow | 9.4.0 | 이미지 처리 |
| python-dotenv | - | 환경 변수 관리 |

## 🔧 개발 도구

### 좌표 선택 도구 (`scripts/coordinate_picker.py`)
- UI 요소의 좌표를 시각적으로 선택
- 상대 좌표 데이터 생성
- 테스트 데이터 작성 지원

### 스크롤 범위 선택 도구 (`utils/scroll_range_picker.py`)
- 스크롤 가능한 영역 정의
- 테스트 시나리오별 스크롤 범위 설정

## ⚠️ 주의사항

### 보안 관련
- `.env` 파일은 절대 Git에 커밋하지 않습니다
- `credentials.json`, `token.pickle` 같은 API 키 파일은 보호됩니다
- `venv` 디렉토리도 Git에 포함되지 않습니다

### 테스트 실행 전 체크리스트
- [ ] Appium 서버가 실행 중인지 확인
- [ ] 디바이스가 연결되어 있는지 확인
- [ ] USB 디버깅이 활성화되어 있는지 확인
- [ ] 환경 변수가 올바르게 설정되어 있는지 확인

## 🐛 문제 해결 가이드

### 1. ModuleNotFoundError: No module named 'utils'
```bash
# 프로젝트 루트 디렉토리에서 테스트를 실행해야 합니다
export PYTHONPATH=$PYTHONPATH:/path/to/moim-app-qa-automation
```

### 2. Appium 서버 연결 실패
- Appium 서버가 실행 중인지 확인
- 포트 충돌 확인 (기본 포트: 4723)
- 환경 변수 `APPIUM_SERVER_URL` 확인

### 3. 디바이스 연결 실패
```bash
# 디바이스 인식 확인
adb devices

# USB 디버깅 활성화 확인
# 설정 > 개발자 옵션 > USB 디버깅
```

### 4. OCR 인식 실패
- 화면 해상도 및 DPI 설정 확인
- EasyOCR 모델 다운로드 상태 확인
- 테스트 이미지 품질 확인

## 🤝 기여 방법

### 1. 이슈 생성
- 🐛 버그 리포트
- 💡 기능 요청
- 📚 문서 개선 제안

### 2. Pull Request
- 코드 스타일 가이드 준수
- 테스트 코드 작성
- 문서 업데이트

### 3. 개발 가이드라인
- Python PEP 8 스타일 가이드 준수
- 테스트 함수명은 `test_` 접두사 사용
- 적절한 주석 및 문서화

## 📈 향후 계획

- [ ] iOS 플랫폼 테스트 완성
- [ ] CI/CD 파이프라인 구축
- [ ] 테스트 커버리지 확대
- [ ] 성능 테스트 추가
- [ ] API 테스트 통합

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요. 
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 