from __future__ import annotations

import cv2
import numpy as np


def normalize_to_uint8(gray: np.ndarray) -> np.ndarray:
    gray = gray.astype(np.float32)
    mn = float(gray.min())
    mx = float(gray.max())
    if mx - mn < 1e-6:
        return np.zeros_like(gray, dtype=np.uint8)
    return ((gray - mn) / (mx - mn) * 255).astype(np.uint8)


def resize_if_large(image_rgb: np.ndarray, max_side: int) -> np.ndarray:
    h, w = image_rgb.shape[:2]
    if max(h, w) <= max_side:
        return image_rgb
    scale = max_side / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
