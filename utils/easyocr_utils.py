# utils/ocr_utils.py

import easyocr
from PIL import Image, ImageEnhance, ImageFilter
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
import os
import time
import cv2
import numpy as np

# EasyOCR Reader 초기화 (한국어 + 영어)
reader = easyocr.Reader(['ko', 'en'], gpu=False)

def tap_coordinates(driver, x, y):
    finger = PointerInput("touch", "finger")
    actions = ActionBuilder(driver, mouse=finger)
    actions.pointer_action.move_to_location(x, y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.pointer_up()
    actions.perform()

def take_screenshot(driver, name):
    path = f"./reports/screenshots/{name}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    print(f"📸 스크린샷 저장됨: {path}")
    return path


def preprocess_image(image_path):
    """이미지를 흑백 및 대비 보정 등으로 전처리"""
    image = Image.open(image_path)
    image = image.convert("L")  # 흑백
    image = image.filter(ImageFilter.SHARPEN)  # 선명하게
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # 대비 증가
    return image

import numpy as np

def extract_text_easyocr(image_path, crop_area=None):
    """
    EasyOCR로 텍스트 추출 (PIL → numpy로 변환)
    """
    image = preprocess_image(image_path)
    if crop_area:
        image = image.crop(crop_area)
    
    np_image = np.array(image)  # ✅ numpy로 변환

    result = reader.readtext(np_image, detail=0, paragraph=True)
    return "\n".join(result).strip()

def is_home_screen_text(text):
    text = text.replace(" ", "").lower()
    keywords = ["홈채널", "홈", "채널", "채녈", "혼채널"]
    return any(k in text for k in keywords)


def ocr_contains_keyword(driver, keyword, shot_name="scroll_step"):
    screenshot_path = take_screenshot(driver, shot_name)
    text = extract_text_easyocr(screenshot_path)
    print(f"📖 OCR 텍스트 추출 결과: {text}")
    return keyword in text

# def scroll_down_w3c(driver, scroll_count=5):
#     print(f"📥 W3C 방식 스크롤 {scroll_count}회 수행 후 OCR로 블록채널 탐색 시작")
#     finger = PointerInput("touch", "finger")

#     for i in range(scroll_count):
#         print(f"↕️ W3C 스크롤 {i+1}/{scroll_count}")
#         actions = ActionBuilder(driver, mouse=finger)
#         actions.pointer_action.move_to_location(500, 1800)  # 안전한 아래 위치
#         actions.pointer_action.pointer_down()
#         actions.pointer_action.pause(0.3)
#         actions.pointer_action.move_to_location(500, 630)   # 중간까지 스와이프
#         actions.pointer_action.pointer_up()
#         actions.perform()
#         time.sleep(1.5)

def scroll_down_w3c(driver, scroll_count=5):
    print(f"📥 사용자 지정 스크롤 좌표로 {scroll_count}회 스크롤 수행")
    finger = PointerInput("touch", "finger")

    # 직접 지정한 안정 좌표
    start_x, start_y = 403, 1953
    end_x, end_y = 361, 412

    for i in range(scroll_count):
        print(f"↕️ W3C 스크롤 {i+1}/{scroll_count}: ({start_x},{start_y}) → ({end_x},{end_y})")

        actions = ActionBuilder(driver, mouse=finger)
        actions.pointer_action.move_to_location(start_x, start_y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.4)  # 탭 오인 방지
        actions.pointer_action.move_to_location(end_x, end_y)
        actions.pointer_action.pause(0.4)  # 이동 후 안정성 확보
        actions.pointer_action.release()
        actions.perform()

        time.sleep(2.0)  # 렌더링 여유


def tap_text_by_ocr(driver, keywords, screenshot_name="ocr_target_search"):
    """
    화면에서 OCR로 여러 후보 키워드 중 하나를 찾아 해당 위치를 탭함
    :param driver: Appium driver
    :param keywords: ['BLOCK_1', 'BLOCK1', 'BLOCL_1'] 등 리스트
    :param screenshot_name: 저장할 스크린샷 이름
    :return: (탭 성공 여부, OCR 전체 텍스트)
    """
    path = take_screenshot(driver, screenshot_name)
    image = preprocess_image(path)
    np_image = np.array(image)

    results = reader.readtext(np_image, detail=1, paragraph=False)  # 좌표 포함 결과
    all_texts = []

    for (bbox, text, prob) in results:
        all_texts.append(text)
        for keyword in keywords:
            if keyword in text:
                # 중심 좌표 계산
                (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
                center_x = int((x1 + x3) / 2)
                center_y = int((y1 + y3) / 2)
                print(f"✅ '{text}' (정답 후보 중 '{keyword}' 포함) 위치: ({center_x}, {center_y}) → 클릭 시도")
                tap_coordinates(driver, center_x, center_y)

                full_text = "\n".join(all_texts)
                print("📝 OCR 전체 추출 텍스트:\n" + full_text)
                return True, full_text

    full_text = "\n".join(all_texts)
    print("❌ 어떤 정답 키워드도 OCR에서 찾지 못함")
    print("📝 OCR 전체 추출 텍스트:\n" + full_text)
    return False, full_text
    