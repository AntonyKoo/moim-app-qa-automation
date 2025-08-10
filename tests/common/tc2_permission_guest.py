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
    scroll_down_w3c, contains_login_dialog
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

# ✅ Forum 네비 이름(변형) 추가
NAV_NAME_VARIANTS.update({
    "FORUM_1": ["FORUM_1","FORUM1","FORUM I","F0RUM_1","FORUM_Ⅰ","FORUMⅠ"],
    "FORUM_2": ["FORUM_2","FORUM2","FORUM II","F0RUM_2","FORUM_Ⅱ","FORUMⅡ"],
    "FORUM_3": ["FORUM_3","FORUM3","FORUM III","FORUM_Ⅲ","FORUMⅢ"],
    "FORUM_4": ["FORUM_4","FORUM4","FORUM IV","FORUM_Ⅳ","FORUMⅣ"],
})

# ---------- Forum 검증 키워드 (플레이스홀더: 테스트 돌리며 교체) ----------
FORUM_KEYS = {
    "list":      ["게시글", "조회", "시간 전", "댓글"],            # TODO: 앱 문구로 조정
    "detail":    ["공유", "복사", "신고", "목록", "댓글", "좋아요"], # TODO: 앱 문구로 조정
    "comments":  ["댓글", "대댓글", "답글"],                       # TODO: 앱 문구로 조정
    "write":     ["글쓰기", "게시하기", "글 작성"],                 # TODO: 앱 문구로 조정
    "commentBox":["댓글을 입력", "댓글 작성", "댓글 쓰기"],         # TODO: 앱 문구로 조정
    "like":      ["좋아요", "추천", "Like"],                       # TODO: 앱 문구로 조정
    "loginReq":  ["로그인이 필요", "로그인", "회원만 이용"],         # TODO: 앱 문구로 조정
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
        x, y = get_abs_point("explore_btn", driver=driver, json_path="utils/rel_position.json")
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

    # ✅ 스크롤 수행 (네비 전체 훑기)
    scroll_down_w3c(driver, scroll_count=9)

    # =========================
    # ✅ BLOCK 1~3
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
    # ✅ Chat Channel 1~3
    # =========================
    chat_specs = [
        {
            "name": "CHAT_1",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_1"],
            "verify_read": ["열심히", "일하는", "수정금지","CHAT_1"],
            # 쓰기 검증은 아래에서 별도(인풋 탭 → 다이얼로그 OCR)로 수행
        },
        {
            "name": "CHAT_2",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_2"],
            "verify_read": ["안녕하세요", "메시지", "님이", "보냈습니다"],
            "verify_write": ["입력", "전송", "쓰기", "보내기"],  # 필요시 이후 CHAT_1 방식으로 변경
        },
        {
            "name": "CHAT_3",
            "nav_keywords": NAV_NAME_VARIANTS["CHAT_3"],
            "verify_read": None,
            "verify_write": None,
        },
    ]

    LOGIN_DIALOG_TEXT = "로그인이 필요합니다. 로그인하시겠습니까?"

    for idx, spec in enumerate(chat_specs, start=1):
        name = spec["name"]
        print(f"💬 {name} 테스트 시작")

        # 1) 사이드네비에서 채팅 채널 '이름'을 OCR로 찾아 탭
        success, ocr_text = tap_text_by_ocr(
            driver,
            spec["nav_keywords"],
            screenshot_name="scroll_final_view"  # 스크린샷 고정
        )
        if not success:
            if name == "CHAT_3":
                print(f"✅ {name}: 채널 접근 불가 (PASS)")
                continue
            raise Exception(f"❌ {name} 위치 탐색 실패")

        # 2) 채널 진입 → 읽기 검증
        time.sleep(3)
        screen = take_screenshot(driver, f"chat{idx}_check")
        ocr_result = extract_text_easyocr(screen)
        print(f"📖 {name} OCR 결과:", ocr_result)

        read_keys = spec.get("verify_read")
        if read_keys:
            if any(k in ocr_result for k in read_keys):
                print(f"✅ {name} 메시지 읽기 가능 (PASS)")
            else:
                print(f"❌ {name} 메시지 읽기 불가 (FAIL)")

        # 3) 쓰기 불가 검증
        if name == "CHAT_1":
            # 메시지 인풋 박스 탭 → 로그인 다이얼로그 노출 확인
            try:
                try:
                    ix, iy = get_abs_point("chat_input_box", driver=driver, json_path="utils/rel_position.json")
                except Exception:
                    ix, iy = abs_by_ratio(driver, 0.50, 0.95)
                tap_coordinates(driver, ix, iy)
                time.sleep(1.5)  # 다이얼로그 뜨는 시간 대기

                dlg_shot = take_screenshot(driver, "chat1_write_dialog")
                dlg_txt = extract_text_easyocr(dlg_shot)
                print("📝 CHAT_1 다이얼로그 OCR:", dlg_txt)

                if contains_login_dialog(dlg_txt):
                    print("✅ CHAT_1 쓰기 불가: 로그인 다이얼로그 확인 (PASS)")
                    ix, iy = get_abs_point("close_btn", driver=driver, json_path="utils/rel_position.json")
                    tap_coordinates(driver, ix, iy)
                else:
                    print("❌ CHAT_1 쓰기 불가 검증 실패: 다이얼로그 문구 미검출 (FAIL)")
            except Exception as e:
                print(f"❌ CHAT_1 쓰기 검증 중 예외: {e}")
        else:
            # 기존 방식 유지(필요 시 CHAT_1 방식으로 교체 예정)
            write_keys = spec.get("verify_write")
            if write_keys:
                if any(k in ocr_result for k in write_keys):
                    print(f"❌ {name} 메시지 쓰기 가능 (FAIL)")
                else:
                    print(f"✅ {name} 메시지 쓰기 불가 (PASS)")

        # 4) 뒤로가기
        try:
            bx, by = get_abs_point("block_channel_back_btn", driver=driver, json_path="utils/rel_position.json")
        except Exception:
            bx, by = abs_by_ratio(driver, 0.15, 0.05)
        tap_coordinates(driver, bx, by)
        time.sleep(2)

    # =========================
    # ✅ Forum Channel 1~4 (게스트)
    # =========================
    forum_specs = [
        # Forum_1 : READ만 다 가능 / UPDATE 다 불가능
        {
            "name": "FORUM_1",
            "nav_keywords": NAV_NAME_VARIANTS["FORUM_1"],
            "expect": {"list": True, "detail": True, "comments": True, "write": False, "commentBox": False, "like": False},
        },
        # Forum_2 : 댓글 읽기만 불가(그 외 READ 가능) / UPDATE 다 불가
        {
            "name": "FORUM_2",
            "nav_keywords": NAV_NAME_VARIANTS["FORUM_2"],
            "expect": {"list": True, "detail": True, "comments": False, "write": False, "commentBox": False, "like": False},
        },
        # Forum_3 : 채널 접근만 가능, 그 외 READ/UPDATE 모두 불가
        {
            "name": "FORUM_3",
            "nav_keywords": NAV_NAME_VARIANTS["FORUM_3"],
            "expect": {"list": False, "detail": False, "comments": False, "write": False, "commentBox": False, "like": False},
        },
        # Forum_4 : 채널 접근 포함 다 불가(리스트에 노출 X) → 탐색 실패여야 PASS
        {
            "name": "FORUM_4",
            "nav_keywords": NAV_NAME_VARIANTS["FORUM_4"],
            "expect": None,
        },
    ]

    for spec in forum_specs:
        name = spec["name"]
        print(f"🧵 {name} 테스트 시작")

        # 1) 사이드네비에서 채널 찾기 (항상 scroll_final_view 기준)
        found, _ = tap_text_by_ocr(
            driver,
            spec["nav_keywords"],
            screenshot_name="scroll_final_view"
        )

        # Forum_4: 보이면 FAIL, 안 보이면 PASS
        if spec["expect"] is None:
            if not found:
                print(f"✅ {name}: 채널 비노출(접근 불가) PASS")
                continue
            else:
                print(f"❌ {name}: 리스트에 보임(FAIL)")
                # 혹시 진입했으면 뒤로
                try:
                    bx, by = get_abs_point("block_channel_back_btn", driver=driver, json_path="utils/rel_position.json")
                except Exception:
                    bx, by = abs_by_ratio(driver, 0.15, 0.05)
                tap_coordinates(driver, bx, by)
                time.sleep(1.2)
                continue

        # Forum_1~3: 반드시 찾아져야 함
        if not found:
            raise Exception(f"❌ {name}: 위치 탐색 실패")

        # 2) 진입 후 OCR 스냅샷
        time.sleep(2)
        scr = take_screenshot(driver, f"{name.lower()}_landing")
        txt = extract_text_easyocr(scr)
        print(f"📝 OCR[{name}] → {txt}")

        exp = spec["expect"]

        # 3) 목록/본문/댓글 가시성 검증 (텍스트 존재 유무만)
        if exp["list"]:
            print("✅ 목록 힌트:", "OK" if any(k in txt for k in FORUM_KEYS["list"]) else "MISS")
        else:
            print("✅ 목록 비노출:", "OK" if not any(k in txt for k in FORUM_KEYS["list"]) else "SEEN")

        if exp["detail"]:
            print("✅ 본문 힌트:", "OK" if any(k in txt for k in FORUM_KEYS["detail"]) else "MISS")
        else:
            print("✅ 본문 비노출:", "OK" if not any(k in txt for k in FORUM_KEYS["detail"]) else "SEEN")

        if exp["comments"]:
            print("✅ 댓글 가시성:", "OK" if any(k in txt for k in FORUM_KEYS["comments"]) else "MISS")
        else:
            print("✅ 댓글 비노출:", "OK" if not any(k in txt for k in FORUM_KEYS["comments"]) else "SEEN")

        # 4) UPDATE 불가(비로그인): 쓰기/댓글입력/좋아요
        print("✅ 글쓰기 없음:", "OK" if not any(k in txt for k in FORUM_KEYS["write"]) else "SEEN")
        print("✅ 댓글입력 없음:", "OK" if not any(k in txt for k in FORUM_KEYS["commentBox"]) else "SEEN")

        # 좋아요 문자열이 보이더라도 로그인 요구 문구 동반 시 불가로 간주
        if any(k in txt for k in FORUM_KEYS["like"]):
            if any(k in txt for k in FORUM_KEYS["loginReq"]):
                print("✅ 좋아요 조작 불가(로그인 요구 감지)")
            else:
                print("⚠️ 좋아요 문자열 감지 — 버튼형 UI인지 추가 확인 권장")
        else:
            print("✅ 좋아요 버튼/문구 비노출")

        # 5) 뒤로가기(기존 키 그대로)
        try:
            bx, by = get_abs_point("block_channel_back_btn", driver=driver, json_path="utils/rel_position.json")
        except Exception:
            bx, by = abs_by_ratio(driver, 0.15, 0.05)
        tap_coordinates(driver, bx, by)
        time.sleep(1.5)

    print("✅ TC2 권한 테스트: 비로그인 사용자 테스트 완료")
