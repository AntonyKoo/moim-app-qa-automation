import cv2
import sys
import os   

def pick_scroll_range(image_path: str):
    if not os.path.exists(image_path):
        print(f"❌ 이미지 경로가 존재하지 않음: {image_path}")
        return

    clicked_points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"👆 클릭한 좌표: x={x}, y={y}")
            clicked_points.append((x, y))

    img = cv2.imread(image_path)
    window_name = '스크롤 범위 추출기 - 시작점과 끝점을 순서대로 클릭하세요 (ESC 또는 Q로 종료)'
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)
    cv2.imshow(window_name, img)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q') or len(clicked_points) >= 2:
            break

    cv2.destroyAllWindows()

    if len(clicked_points) < 2:
        print("❗ 시작점과 끝점을 모두 클릭하지 않았습니다.")
        return

    (x1, y1), (x2, y2) = clicked_points[:2]
    print("\n✅ 스크롤에 사용할 좌표:")
    print(f"📍 시작 위치: x={x1}, y={y1}")
    print(f"📍 종료 위치: x={x2}, y={y2}")

    print("\n📌 아래 코드를 스크롤 함수에 넣어 사용하세요:")
    print(f"start_x, start_y = {x1}, {y1}")
    print(f"end_x, end_y = {x2}, {y2}")

# CLI 실행
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ 사용법: python utils/scroll_range_picker.py [이미지경로]")
    else:
        pick_scroll_range(sys.argv[1])