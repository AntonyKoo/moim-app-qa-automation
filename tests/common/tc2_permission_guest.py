import time
import easyocr
from selenium.webdriver.common.by import By

# ✅ 좌표 계산: coordinate_picker 대신 coordinates 사용
from utils.coordinates import (
    get_abs_point,      # JSON 키 기반 절대좌표
    get_device_resolution,
    rel_to_abs          # 비율 → 절대좌표 변환
)

from utils.easyocr_utils import (
    extract_text_easyocr, is_home_screen_text,
    tap_coordinates, take_screenshot, tap_text_by_ocr,
    scroll_down_w3c
)

# ---------- OCR ----------
reader = easyocr.Reader(['ko', 'en'], gpu=False)

# ---------- 네비게이션용 이름 변형 사전 (OCR 흔오류 포함) ----------
NAV_NAME_VARIANTS = {
    # BLOCK 채널
    "BLOCK_1": ["BLOCK_1", "BLOCK1", "BLOCK I", "BLOCKI", "BLOCL_1", "BLOCK_Ⅰ", "BLOCKⅠ"],
    "BLOCK_2": ["BLOCK_2", "BLOCK2", "BLOCK II", "BLOCKII", "BLOCL_2", "BLOCK_Ⅱ", "BLOCKⅡ"],
    "BLOCK_3": ["BLOCK_3", "BLOCK3", "BLOCK III", "BLOCKIII", "BLOCL_3", "BLOCK_Ⅲ", "BLOCKⅢ"],
    # CHAT 채널
    "CHAT_1": ["CHAT_1","CHAT1","CHAT I","CHATI","CH4T_1","CHAT_Ⅰ","CHATⅠ","CHAT_I","CHATl","CHAT|"], 
    "CHAT_2": ["CHAT_2","CHAT2","CHAT II","CHATII","CH4T_2","CHAT_Ⅱ","CHATⅡ", "CHAT_II","CHATll","CHAT||"],
    "CHAT_3": ["CHAT_3","CHAT3","CHAT III","CHATIII","CH4T_3","CHAT_Ⅲ","CHATⅢ", "CHAT_III"],
}

# 비율 좌표를 즉시 절대좌표로 변환 (기존 코드와 호환용)
def abs_by_ratio(driver, rx: float, ry: float):
    w, h = get_device_resolution(driver)
    return rel_to_abs(rx, ry, (w, h))

def run_tc2_permission_guest(driver):
    print("🔍 TC2 권한 허용 + 게스트 접근 테스트 시작...")

    driver.implicitly_wait(10)
    time.sleep(5)

    # ✅ 알림 권한 팝업 허용
    try:
        allow_button = driver.find_element(By.ID, "com.android.permissioncontroller:id/permission_allow_button")
        allow_button.click()
        print("✅ 알림 권한 허용 클릭 완료")
        time.sleep(3)
    except Exception:
        print("ℹ️ 알림 권한 팝업 없음")
        time.sleep(1)

    # ✅ 둘러보기 버튼 클릭
    try:
        x, y = get_abs_point("guest_explore_button", driver=driver, json_path="utils/rel_position.json")
        print("📍 둘러보기 버튼(JSON 키) 클릭 좌표:", x, y)
    except Exception:
        x, y = abs_by_ratio(driver, 0.22, 0.8705)
        print(f"📍 둘러보기 버튼(비율) 클릭: x={x}, y={y}")
    tap_coordinates(driver, x, y)
    print("👆 둘러보기 버튼 클릭 완료")
    time.sleep(3)

    # ✅ 팝업 배너 닫기 (좌표 탭)
    try:
        try:
            px, py = get_abs_point("popup_banner_close_btn", driver=driver, json_path="utils/rel_position.json")
        except Exception:
            px, py = abs_by_ratio(driver, 0.75, 0.95)
        tap_coordinates(driver, px, py)
        print("✅ 팝업 닫기 완료")
        time.sleep(3)
    except Exception:
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

    # ✅ 사이드 네비 열기
    print("📂 사이드 네비 열기")
    try:
        sx, sy = get_abs_point("side_nav_open", driver=driver, json_path="utils/rel_position.json")
    except Exception:
        sx, sy = abs_by_ratio(driver, 0.20, 0.95)
    tap_coordinates(driver, sx, sy)
    time.sleep(3)

    # ✅ 스크롤 수행
    scroll_down_w3c(driver, scroll_count=9)

    # =========================
    # ✅ BLOCK 1~3 (네비 탐색 → 진입 후 검증)
    # =========================
    block_order = ["BLOCK_1", "BLOCK_2", "BLOCK_3"]

    for idx, block_name in enumerate(block_order, start=1):
        block_keywords = NAV_NAME_VARIANTS[block_name]  # 네비에서 찾을 이름 후보

        # 1) 사이드네비에서 채널 '이름'을 OCR로 찾아 탭
        success, ocr_text = tap_text_by_ocr(driver, block_keywords, screenshot_name=f"block{idx}_ocr")
        if not success:
            if block_name == "BLOCK_3":
                print("✅ BLOCK_3: 채널 접근 불가 (PASS)")
                continue
            raise Exception(f"❌ {block_name} 위치 탐색 실패")

        # 2) 진입 후 화면 캡처 → 내용 검증
        time.sleep(3)
        screen = take_screenshot(driver, f"block{idx}_check")
        ocr_result = extract_text_easyocr(screen)
        print(f"📖 {block_name} OCR 결과:", ocr_result)

        if block_name == "BLOCK_1":
            if "결제 정보" in ocr_result:
                print("✅ BLOCK_1 테스트 PASS")
            else:
                print("❌ BLOCK_1 테스트 FAIL")
                take_screenshot(driver, "block1_fail")
        elif block_name == "BLOCK_2":
            if "화면을" in ocr_result:
                print("❌ BLOCK_2: 읽기 가능 (FAIL)")
                take_screenshot(driver, "block2_fail")
            else:
                print("✅ BLOCK_2: 읽기 불가 (PASS)")

        # 3) 뒤로가기
        try:
            bx, by = get_abs_point("block_channel_back_btn", driver=driver, json_path="utils/rel_position.json")
        except Exception:
            bx, by = abs_by_ratio(driver, 0.15, 0.05)
        tap_coordinates(driver, bx, by)
        time.sleep(2)

    # =========================
    # ✅ Chat Channel 1~3 (네비 탐색 → 진입 후 검증)
    # =========================
    chat_specs = [
        {
            "name": "CHAT_1",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_1"],              # 사이드네비에서 찾을 이름
            "verify_read": ["메시지를", "보내려면", "로그인을"],       # 진입 후 '읽기' 판단 텍스트
            "verify_write": ["입력", "전송", "쓰기", "보내기"],        # 진입 후 '쓰기' 판단 텍스트
        },
        {
            "name": "CHAT_2",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_2"],
            "verify_read": ["안녕하세요", "메시지", "님이", "보냈습니다"],
            "verify_write": ["입력", "전송", "쓰기", "보내기"],
        },
        {
            "name": "CHAT_3",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_3"],
            "verify_read": None,   # 존재 자체가 없으면 PASS 처리 의도
            "verify_write": None,
        },
    ]

    for idx, spec in enumerate(chat_specs, start=1):
        name = spec["name"]
        print(f"💬 {name} 테스트 시작")

        # 1) 사이드네비에서 채팅 채널 '이름'을 OCR로 찾아 탭
        #    ※ 동일 스크린샷 파일명으로 고정해서 같은 화면 기준으로만 탐색
        success, ocr_text = tap_text_by_ocr(
            driver,
            spec["nav_keywords"],
            screenshot_name="scroll_fianl_view"  # ← 오탈자 포함 원문 유지
        )
        if not success:
            if name == "CHAT_3":
                print(f"✅ {name}: 채널 접근 불가 (PASS)")
                continue
            raise Exception(f"❌ {name} 위치 탐색 실패")

        # 2) 채널 진입 → 내용 검증
        time.sleep(3)
        screen = take_screenshot(driver, f"chat{idx}_check")
        ocr_result = extract_text_easyocr(screen)
        print(f"📖 {name} OCR 결과:", ocr_result)

        # 읽기 가능 여부
        read_keys = spec["verify_read"]
        if read_keys:
            if any(k in ocr_result for k in read_keys):
                print(f"✅ {name} 메시지 읽기 가능 (PASS)")
            else:
                print(f"❌ {name} 메시지 읽기 불가 (FAIL)")

        # 쓰기 가능 여부
        write_keys = spec["verify_write"]
        if write_keys:
            if any(k in ocr_result for k in write_keys):
                print(f"❌ {name} 메시지 쓰기 가능 (FAIL)")
            else:
                print(f"✅ {name} 메시지 쓰기 불가 (PASS)")

        # 3) 뒤로가기
        try:
            bx, by = get_abs_point("block_channel_back_btn", driver=driver, json_path="utils/rel_position.json")
        except Exception:
            bx, by = abs_by_ratio(driver, 0.15, 0.05)
        tap_coordinates(driver, bx, by)
        time.sleep(2)

    print("✅ TC2 권한 테스트: 비로그인 사용자 테스트 완료")
