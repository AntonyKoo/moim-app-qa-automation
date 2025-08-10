import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.driver_setup import setup_android_driver
from tests.common.tc2_permission_guest import run_tc2_permission_guest

driver = setup_android_driver()

try:
    run_tc2_permission_guest(driver)
finally:
    driver.quit()