import os
import time
from datetime import datetime
from PIL import Image
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

def login_as_user(driver, email):
    # 로그인 페이지 이동 + 입력
    pass

def open_block_channel(driver, block_name):
    # 채널 리스트에서 해당 채널 검색 → 접근 시도 → 블록 내용 존재 여부 확인
    # return (채널 접근 성공 여부, 블록 읽기 가능 여부)
    pass

def take_screenshot(driver, test_name):
    """
    테스트 실행 중 스크린샷을 찍고 저장합니다.
    
    Args:
        driver: Appium WebDriver 인스턴스
        test_name: 테스트 이름 (파일명으로 사용)
    
    Returns:
        str: 저장된 스크린샷의 파일 경로
    """
    # reports/screenshots 디렉토리가 없으면 생성
    screenshot_dir = os.path.join('reports', 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # 파일명 생성 (테스트명_타임스탬프.png)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{test_name}_{timestamp}.png"
    filepath = os.path.join(screenshot_dir, filename)
    
    # 스크린샷 촬영 및 저장
    driver.get_screenshot_as_file(filepath)
    print(f"스크린샷 저장됨: {filepath}")
    
    return filepath

def log_result_to_sheet(test_name, status, error_message=None, screenshot_path=None):
    """
    테스트 결과를 Google Sheets에 기록합니다.
    
    Args:
        test_name: 테스트 이름
        status: 테스트 상태 ('PASS' 또는 'FAIL')
        error_message: 실패 시 에러 메시지 (선택사항)
        screenshot_path: 스크린샷 파일 경로 (선택사항)
    """
    # Google Sheets API 인증
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    RANGE_NAME = 'Test Results!A:E'
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('sheets', 'v4', credentials=creds)
    
    # 테스트 결과 데이터 준비
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values = [[timestamp, test_name, status, error_message or '', screenshot_path or '']]
    
    body = {
        'values': values
    }
    
    # Google Sheets에 데이터 추가
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"테스트 결과가 Google Sheets에 기록되었습니다: {test_name}")
    except Exception as e:
        print(f"Google Sheets 기록 중 오류 발생: {str(e)}")

def wait_for_element(driver, by, value, timeout=10):
    """
    요소가 나타날 때까지 대기합니다.
    
    Args:
        driver: Appium WebDriver 인스턴스
        by: 요소를 찾는 방법 (By.ID, By.XPATH 등)
        value: 요소의 값
        timeout: 최대 대기 시간 (초)
    
    Returns:
        WebElement: 찾은 요소
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            element = driver.find_element(by, value)
            return element
        except:
            time.sleep(0.5)
    raise TimeoutError(f"요소를 찾을 수 없습니다: {value}")

def is_element_present(driver, by, value):
    """
    요소가 존재하는지 확인합니다.
    
    Args:
        driver: Appium WebDriver 인스턴스
        by: 요소를 찾는 방법 (By.ID, By.XPATH 등)
        value: 요소의 값
    
    Returns:
        bool: 요소 존재 여부
    """
    try:
        driver.find_element(by, value)
        return True
    except:
        return False
