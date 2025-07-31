# utils/coordinate_picker.py

import cv2
import sys
import os

def pick_coordinates(image_path: str):
    if not os.path.exists(image_path):
        print(f"❌ 이미지 경로가 존재하지 않음: {image_path}")
        return

    clicked_points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"👆 클릭한 좌표: x={x}, y={y}")
            clicked_points.append((x, y))

    img = cv2.imread(image_path)
    window_name = '좌표 추출기 (q 또는 ESC 키로 종료)'
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)
    cv2.imshow(window_name, img)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cv2.destroyAllWindows()

    print("✅ 클릭한 좌표 목록:", clicked_points)

# CLI 실행
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ 사용법: python utils/coordinate_picker.py [이미지경로]")
    else:
        pick_coordinates(sys.argv[1])