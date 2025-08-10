from __future__ import annotations
import os, json
from typing import Dict, Tuple, Optional, Any

Json = Dict[str, Any]

def get_device_resolution(driver) -> Tuple[int, int]:
    """Appium Driver에서 현재 디바이스 해상도(px)를 가져옴"""
    size = driver.get_window_size()
    
    return int(size["width"]), int(size["height"])

def _load_json(path: str) -> Json:
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _extract_points_and_ref(data: Json) -> Tuple[Dict[str, Dict[str, float]], Tuple[int, int]]:
    """
    rel_position.json에서 포인트와 기준 해상도 추출.
    - 포맷 A: top-level에 key들이 직접 존재
    - 포맷 B: 'points' 아래에 key들이 존재
    - 값 형태:
      - {"x": 0.5, "y": 0.5}
      - [0.5, 0.5] 또는 (0.5, 0.5)
    """
    ref = data.get("reference") or data.get("_reference") or {}
    ref_w, ref_h = int(ref.get("width", 0)), int(ref.get("height", 0))
    if not (ref_w and ref_h):
        raise ValueError("reference.width/height가 json에 필요합니다.")

    source_points = data.get("points") if isinstance(data.get("points"), dict) else {
        k: v for k, v in data.items()
        if k not in ("reference", "_reference") and isinstance(v, (dict, list, tuple))
    }

    valid: Dict[str, Dict[str, float]] = {}
    for name, val in source_points.items():
        # dict 형태 {"x": .., "y": ..}
        if isinstance(val, dict) and "x" in val and "y" in val:
            valid[name] = {"x": float(val["x"]), "y": float(val["y"])}
            continue
        # list/tuple 형태 [x, y]
        if isinstance(val, (list, tuple)) and len(val) == 2:
            valid[name] = {"x": float(val[0]), "y": float(val[1])}
            continue

    return valid, (ref_w, ref_h)

def rel_to_abs(
    rel_x: float,
    rel_y: float,
    current_size: Tuple[int, int],
    reference_size: Optional[Tuple[int, int]] = None,
    clamp: bool = True,
) -> Tuple[int, int]:
    """
    상대좌표→절대좌표(px).
    - 비율모드: 0~1 범위면 비율로 계산
    - 스케일모드: 1 초과 값이면 reference_size 기준 픽셀로 판단 후 현재 해상도로 스케일
    """
    cur_w, cur_h = current_size
    if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
        abs_x = int(round(rel_x * cur_w))
        abs_y = int(round(rel_y * cur_h))
    else:
        if not reference_size:
            raise ValueError("reference_size가 필요합니다 (rel_x/y가 비율이 아닐 때).")
        ref_w, ref_h = reference_size
        if ref_w <= 0 or ref_h <= 0:
            raise ValueError("reference_size가 유효하지 않습니다.")
        abs_x = int(round((rel_x / ref_w) * cur_w))
        abs_y = int(round((rel_y / ref_h) * cur_h))

    if clamp:
        abs_x = max(1, min(cur_w - 1, abs_x))
        abs_y = max(1, min(cur_h - 1, abs_y))
    return abs_x, abs_y

def get_abs_point(
    key: str,
    *,
    driver=None,
    current_size: Optional[Tuple[int, int]] = None,
    json_path: str = "utils/rel_position.json",
) -> Tuple[int, int]:
    """
    rel_position.json에서 key를 찾아 현재 디바이스 절대좌표(px)로 반환.
    """
    data = _load_json(json_path)
    points, (ref_w, ref_h) = _extract_points_and_ref(data)
    if key not in points:
        raise KeyError(f"'{key}'가 {json_path}에 없습니다. 존재 키 예: {list(points.keys())[:10]}")

    rel = points[key]
    if current_size is None:
        if driver is None:
            raise ValueError("driver 또는 current_size 둘 중 하나는 필요합니다.")
        current_size = get_device_resolution(driver)

    return rel_to_abs(rel["x"], rel["y"], current_size=current_size, reference_size=(ref_w, ref_h))