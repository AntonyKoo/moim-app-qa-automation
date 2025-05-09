from appium import webdriver
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options().load_capabilities({
    'platformName': 'Android',
    'automationName': 'UiAutomator2',
    'deviceName': 'Test Device'
})

try:
    driver = webdriver.Remote('http://localhost:4723', options=options)
    print("Appium 연결 성공")
    driver.quit()
except Exception as e:
    print(f"오류 발생: {e}")