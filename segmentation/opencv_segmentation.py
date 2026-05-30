
from __future__ import annotations

import cv2
import numpy as np
from skimage import measure, morphology

def normalize_to_uint8(gray: np.ndarray) -> np.ndarray:
    gray = gray.astype(np.float32)
    mn = float(gray.min())
    mx = float(gray.max())
    if mx - mn < 1e-6:
        return np.zeros_like(gray, dtype=np.uint8)
    return ((gray - mn) / (mx - mn) * 255).astype(np.uint8)

def segment_opencv(
    image_rgb: np.ndarray,
    blur_kernel: int = 5,
    min_object_area: int = 120,
    use_adaptive_threshold: bool = True,
    invert_threshold: bool = False,
) -> np.ndarray:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    gray = normalize_to_uint8(gray)

    if blur_kernel % 2 == 0:
        blur_kernel += 1

    blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
    threshold_type = cv2.THRESH_BINARY_INV if not invert_threshold else cv2.THRESH_BINARY

    if use_adaptive_threshold:
        binary = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            threshold_type,
            51,
            2,
        )
    else:
        _, binary = cv2.threshold(blurred, 0, 255, threshold_type + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    mask_bool = binary > 0
    mask_bool = morphology.remove_small_objects(mask_bool, min_size=min_object_area)
    mask_bool = morphology.remove_small_holes(mask_bool, area_threshold=min_object_area)

    return measure.label(mask_bool, connectivity=2).astype(np.int32)
