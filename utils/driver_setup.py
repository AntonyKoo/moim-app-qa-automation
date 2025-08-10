import os
from appium import webdriver
from dotenv import load_dotenv
from appium.options.android import UiAutomator2Options

# .env 파일 로드
load_dotenv()

# 안드로이드 드라이버 설정
def setup_android_driver():
    desired_caps = {
        'platformName': os.environ.get('APPIUM_PLATFORM_NAME', 'Android'),
        'automationName': os.environ.get('APPIUM_AUTOMATION_NAME', 'UiAutomator2'),
        'deviceName': os.environ.get('APPIUM_DEVICE_NAME', 'Test Device'),
        'udid': os.environ.get('APPIUM_UDID'),
        'appPackage': os.environ.get('APPIUM_APP_PACKAGE'),
        'appActivity': os.environ.get('APPIUM_APP_ACTIVITY'),
        'noReset': os.environ.get('APPIUM_NO_RESET', 'false').lower() == 'true'
    }

    return webdriver.Remote(
        command_executor=os.environ.get('APPIUM_SERVER_URL', 'http://localhost:4723'),
        options=UiAutomator2Options().load_capabilities(desired_caps)
    )