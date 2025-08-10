#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 연결된 ANDROID 디바이스 화면을 캡처해 미리보기로 띄우고,
마우스 클릭 위치를 '디바이스 절대 좌표(px)' 및 '상대 좌표(비율)'로 출력합니다.

키보드:
  r  : 화면 새로고침 (디바이스 재캡처)
  esc / f / q : 프로그램 종료
실행 방법: python3 scripts/coordinate_picker.py
"""

import cv2
import sys
import subprocess
import numpy as np
from shutil import which
from typing import Optional, Tuple, List
from io import BytesIO

try:
    from PIL import Image  # Pillow
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

WINDOW_NAME = "좌표 추출기 (r: 새로고침, esc/f/q: 종료)"
MAX_PREVIEW_W = 1280
MAX_PREVIEW_H = 2560

# ---------- ADB helpers ----------
def adb_available() -> bool:
    return which("adb") is not None

def run(cmd: list, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)

def get_connected_device() -> Optional[str]:
    """연결된 첫 번째 ADB 디바이스 ID 반환 (없으면 None)"""
    try:
        proc = run(["adb", "devices"])
        if proc.returncode != 0:
            return None
        lines = proc.stdout.decode("utf-8", errors="ignore").strip().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                return parts[0]
        return None
    except Exception:
        return None

def _decode_png_bytes(data: bytes) -> Optional[np.ndarray]:
    """PNG 바이트를 OpenCV로 디코딩. 실패 시 줄바꿈 정규화 후 재시도, 그 후 Pillow fallback."""
    # 1) 그대로 시도
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is not None:
        return img

    # 2) CRLF 정규화 후 재시도
    data2 = data.replace(b"\r\n", b"\n").replace(b"\r\r\n", b"\n")
    if data2 != data:
        arr2 = np.frombuffer(data2, dtype=np.uint8)
        img2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)
        if img2 is not None:
            return img2

    # 3) Pillow fallback (RGB→BGR)
    if PIL_AVAILABLE:
        try:
            with Image.open(BytesIO(data2)) as im:
                im = im.convert("RGB")
                np_im = np.array(im)  # RGB
                bgr = cv2.cvtColor(np_im, cv2.COLOR_RGB2BGR)
                return bgr
        except Exception:
            pass

    return None

def capture_screenshot(device_id: Optional[str]) -> np.ndarray:
    """
    현재 디바이스 스크린샷을 numpy(BGR)로 반환.
    - 우선 exec-out으로 시도, 실패 시 shell로 Fallback
    - CRLF 정규화 및 Pillow fallback 지원
    """
    # 1) exec-out
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += ["exec-out", "screencap", "-p"]

    proc = run(cmd, timeout=20)
    data = proc.stdout if proc.returncode == 0 else b""

    img = _decode_png_bytes(data) if data else None
    if img is not None:
        return img

    # 2) shell fallback
    cmd2 = ["adb"]
    if device_id:
        cmd2 += ["-s", device_id]
    cmd2 += ["shell", "screencap", "-p"]
    proc2 = run(cmd2, timeout=20)
    data2 = proc2.stdout if proc2.returncode == 0 else b""
    img2 = _decode_png_bytes(data2) if data2 else None
    if img2 is not None:
        return img2

    # 실패 시 에러 메시지 정리
    err_msg = proc.stderr.decode("utf-8", errors="ignore") if proc.stderr else ""
    err_msg2 = proc2.stderr.decode("utf-8", errors="ignore") if proc2.stderr else ""
    raise RuntimeError(
        "스크린샷 디코딩 실패: OpenCV/Pillow 모두 PNG 바이트를 해석하지 못했습니다.\n"
        f"[exec-out stderr] {err_msg or 'None'}\n"
        f"[shell stderr] {err_msg2 or 'None'}\n"
        "※ 해결팁: adb 권한/연결 확인, Pillow 설치(pip install pillow), 다른 기기/케이블 테스트"
    )

# ---------- UI helpers ----------
def make_preview(img: np.ndarray) -> Tuple[np.ndarray, float]:
    """원본을 미리보기 크기로 축소한 이미지와 scale을 반환 (preview = original * scale)."""
    h, w = img.shape[:2]
    scale_w = min(1.0, MAX_PREVIEW_W / float(w))
    scale_h = min(1.0, MAX_PREVIEW_H / float(h))
    scale = min(scale_w, scale_h)
    if scale < 1.0:
        preview = cv2.resize(img, (int(w * scale), int(h * scale)))
    else:
        preview = img.copy()
    return preview, scale

def main():
    if not adb_available():
        print("❌ 'adb'를 찾을 수 없습니다. ANDROID_HOME/PATH 설정을 확인하세요.")
        sys.exit(1)

    device_id = get_connected_device()
    if not device_id:
        print("❌ 연결된 ADB 디바이스가 없습니다. 'adb devices'로 연결 상태를 확인하세요.")
        sys.exit(1)
    print(f"🔗 연결 디바이스: {device_id}")

    # 현재 디바이스 해상도 (스크린샷 기준)
    try:
        img = capture_screenshot(device_id)
    except Exception as e:
        print(f"❌ 첫 스크린샷 실패: {e}")
        if not PIL_AVAILABLE:
            print("ℹ️ Pillow가 설치되어 있지 않다면 'pip install pillow' 후 다시 시도해 주세요.")
        sys.exit(1)

    device_h, device_w = img.shape[:2]  # 절대좌표 → 상대좌표 환산에 사용
    preview, scale = make_preview(img)
    clicked_points_abs: List[Tuple[int, int]] = []
    clicked_points_rel: List[Tuple[float, float]] = []

    def click_event(event, x, y, flags, params):
        nonlocal device_w, device_h
        if event == cv2.EVENT_LBUTTONDOWN:
            if scale <= 0:
                print("⚠️ scale 계산 오류")
                return
            # 미리보기 좌표 → 원본(디바이스) 절대좌표
            abs_x = int(round(x / scale))
            abs_y = int(round(y / scale))
            clicked_points_abs.append((abs_x, abs_y))

            # 절대좌표 → 상대좌표(0~1)
            # (0.0 ~ 1.0 사이 float, 소수점 6자리 표시)
            rel_x = abs_x / float(device_w) if device_w else 0.0
            rel_y = abs_y / float(device_h) if device_h else 0.0
            clicked_points_rel.append((rel_x, rel_y))

            print(f"👆 클릭(디바이스 기준): x={abs_x}, y={abs_y}")
            print(f"   상대좌표(비율):     x={rel_x:.6f}, y={rel_y:.6f}")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WINDOW_NAME, click_event)
    cv2.imshow(WINDOW_NAME, preview)

    while True:
        key = cv2.waitKey(30) & 0xFF
        if key == ord('r'):
            try:
                img = capture_screenshot(device_id)
                device_h, device_w = img.shape[:2]  # 해상도 갱신
                preview, scale = make_preview(img)
                cv2.imshow(WINDOW_NAME, preview)
                print(f"🔄 화면 새로고침 완료 (W={device_w}, H={device_h})")
            except Exception as e:
                print(f"❌ 새로고침 실패: {e}")
        elif key in (27, ord('q'), ord('f')):
            break

    cv2.destroyAllWindows()
    print("✅ 클릭한 좌표 목록(디바이스 기준 px):", clicked_points_abs)
    print("✅ 클릭한 좌표 목록(상대 비율 0~1):", [ (round(x,6), round(y,6)) for x,y in clicked_points_rel ])

if __name__ == "__main__":
    # OpenCV 설치 체크
    try:
        _ = cv2.__version__
    except Exception:
        print("❌ OpenCV가 설치되지 않았거나 불완전합니다. pip install opencv-python")
        sys.exit(1)
    main()
