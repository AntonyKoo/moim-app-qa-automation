import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.touch_action import TouchAction
from dotenv import load_dotenv
import time

# .env 파일 로드 (Desired Capabilities 설정)
load_dotenv()

options = UiAutomator2Options()
options.platform_name = os.environ.get('APPIUM_PLATFORM_NAME', 'Android')
options.automation_name = os.environ.get('APPIUM_AUTOMATION_NAME', 'UiAutomator2')
options.device_name = os.environ.get('APPIUM_DEVICE_NAME', 'Test Device')
options.udid = os.environ.get('APPIUM_UDID')
options.app_package = os.environ.get('APPIUM_APP_PACKAGE')
options.app_activity = os.environ.get('APPIUM_APP_ACTIVITY')
options.no_reset = os.environ.get('APPIUM_NO_RESET', 'false').lower() == 'true'

appium_server_url = os.environ.get('APPIUM_SERVER_URL', 'http://localhost:4723')

driver = None

try:
    # Appium 서버에 연결 (options 객체 전달)
    driver = webdriver.Remote(appium_server_url, options=options)
    driver.implicitly_wait(10)  # 암묵적 대기 설정 (최대 10초)

    time.sleep(5)  # 앱 로딩 대기 (필요에 따라 조정)

    # "로그인" 버튼 좌표 탭 (Appium Inspector에서 확인한 좌표로 변경해야 합니다.)
    login_x = 478   # 실제 X 좌표로 변경
    login_y = 1942  # 실제 Y 좌표로 변경
    actions = TouchAction(driver)
    actions.tap(x=login_x, y=login_y).perform()
    print(f"로그인 버튼 좌표 (x={login_x}, y={login_y}) 탭")

    # 여기에 추가적인 테스트 코드를 작성할 수 있습니다.

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    if driver:
        driver.quit()