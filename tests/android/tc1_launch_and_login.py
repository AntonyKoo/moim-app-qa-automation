import os
import time
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

# .env 파일 로드
load_dotenv()

# Appium 옵션 구성
options = UiAutomator2Options()
options.platform_name = os.environ.get('APPIUM_PLATFORM_NAME', 'Android')
options.automation_name = os.environ.get('APPIUM_AUTOMATION_NAME', 'UiAutomator2')
options.device_name = os.environ.get('APPIUM_DEVICE_NAME', 'Test Device')
options.udid = os.environ.get('APPIUM_UDID')
options.app_package = os.environ.get('APPIUM_APP_PACKAGE')
options.app_activity = os.environ.get('APPIUM_APP_ACTIVITY')
options.no_reset = os.environ.get('APPIUM_NO_RESET', 'false').lower() == 'true'

# Appium 서버 주소
appium_server_url = os.environ.get('APPIUM_SERVER_URL', 'http://localhost:4723')

driver = None

try:
    # Appium 드라이버 시작
    driver = webdriver.Remote(command_executor=appium_server_url, options=options)
    driver.implicitly_wait(10)

    time.sleep(5)  # 앱 첫 화면 로딩 대기

    # ✅ 1단계: 알림 권한 팝업에서 "허용" 버튼 클릭
    try:
        allow_button = driver.find_element(By.ID, "com.android.permissioncontroller:id/permission_allow_button")
        allow_button.click()
        print("알림 권한 허용 버튼 클릭 완료")
        time.sleep(1)
    except Exception as e:
        print("허용 버튼이 표시되지 않음 (이미 권한 있음 또는 팝업 없음)")

    # ✅ 2단계: 로그인 버튼 좌표 탭 (W3C 방식 - 문자열 사용)
    login_x = 478
    login_y = 1942

    finger = PointerInput("touch", "finger")  # Enum 대신 문자열 직접 사용
    actions = ActionBuilder(driver, mouse=finger)
    actions.pointer_action.move_to_location(login_x, login_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.pointer_up()
    actions.perform()

    print(f"로그인 버튼 좌표 (x={login_x}, y={login_y}) 탭 완료")

except Exception as e:
    print(f"오류 발생: {e}")

# finally:
#     if driver:
#         driver.quit()
