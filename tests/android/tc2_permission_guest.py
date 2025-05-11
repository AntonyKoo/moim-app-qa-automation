import os
import time
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from utils.easyocr_utils import extract_text_easyocr, is_home_screen_text, tap_coordinates, take_screenshot, tap_text_by_ocr, scroll_down_w3c
import easyocr

# -------------------------
# 1. 환경 변수 로드
# -------------------------
load_dotenv()

# -------------------------
# 2. EasyOCR 초기화
# -------------------------
reader = easyocr.Reader(['ko', 'en'], gpu=False)

# -------------------------
# 3. Appium 옵션 설정
# -------------------------
options = UiAutomator2Options()
options.platform_name = os.environ.get('APPIUM_PLATFORM_NAME', 'Android')
options.automation_name = os.environ.get('APPIUM_AUTOMATION_NAME', 'UiAutomator2')
options.device_name = os.environ.get('APPIUM_DEVICE_NAME', 'Test Device')
options.udid = os.environ.get('APPIUM_UDID')
options.app_package = os.environ.get('APPIUM_APP_PACKAGE')
options.app_activity = os.environ.get('APPIUM_APP_ACTIVITY')
options.no_reset = os.environ.get('APPIUM_NO_RESET', 'false').lower() == 'true'
appium_server_url = os.environ.get('APPIUM_SERVER_URL', 'http://localhost:4723')

# -------------------------
# 4. 실행 시작
# -------------------------
driver = None
try:
    print("🚀 Appium 드라이버 연결 시도...")
    driver = webdriver.Remote(command_executor=appium_server_url, options=options)
    driver.implicitly_wait(10)
    time.sleep(5)

    # ✅ 알림 권한 팝업 허용
    try:
        allow_button = driver.find_element(By.ID, "com.android.permissioncontroller:id/permission_allow_button")
        allow_button.click()
        print("✅ 알림 권한 허용 클릭 완료")
        time.sleep(3)
    except:
        print("ℹ️ 알림 권한 팝업 없음")
        time.sleep(1)

    # ✅ 둘러보기 버튼 클릭
    tap_coordinates(driver, 483, 2092)
    print("👆 둘러보기 버튼 클릭 완료")
    time.sleep(3)

    # ✅ 팝업 배너 닫기 (좌표 탭)
    try:
        tap_coordinates(driver, 251, 1581)
        print("✅ 팝업 닫기 완료")
        time.sleep(3)
    except:
        print("ℹ️ 팝업 닫기 시도 실패")
        time.sleep(1)

    # ✅ OCR 기반 홈 화면 진입 판단
    screenshot_path = take_screenshot(driver, "guest_home_screen")
    time.sleep(4)

    ocr_text = extract_text_easyocr(screenshot_path)
    print("📝 OCR 추출 텍스트:", ocr_text)

    if is_home_screen_text(ocr_text):
        print("✅ OCR로 홈 화면 진입 성공")
    else:
        print("❌ OCR로 홈 화면 진입 실패")
        take_screenshot(driver, "guest_home_fail")

    # ✅ 사이드 네비게이션 열기
    print("📂 사이드 네비 열기 좌표 탭")
    time.sleep(4)
    tap_coordinates(driver, 81, 2165)
    time.sleep(3)

    # ✅ 일정 횟수 스크롤만 수행 (키워드 판단 안 함)
    scroll_down_w3c(driver, scroll_count=5)

    block_keywords = ["BLOCK_1", "BLOCK1", "BLOCK_I","BLOCKI"]

    # ✅ BLOCK_1 텍스트 위치 찾아 클릭
    success, ocr_text = tap_text_by_ocr(driver, block_keywords, screenshot_name="block1_ocr")
    if not success:
        raise Exception("❌ BLOCK_1 위치 탐색 실패")
    time.sleep(3)

    # ✅ 진입 후 판단
    block1_screen = take_screenshot(driver, "block1_check")
    ocr_result = extract_text_easyocr(block1_screen)

    print("📖 BLOCK_1 진입 화면 OCR 결과:")
    print(ocr_result)

    if "결제 정보" in ocr_result:
        print("✅ BLOCK_1 테스트 결과: 접근 가능 + 읽기 가능 (PASS)")
    else:
        print("❌ BLOCK_1 테스트 결과: '결제 정보' 미포함 (FAIL)")
        take_screenshot(driver, "block1_fail")

except Exception as e:
    print(f"❌ 실행 중 오류 발생: {e}")

# finally:
#     if driver:
#         driver.quit()
