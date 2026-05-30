
from __future__ import annotations

import numpy as np
from skimage import segmentation

def create_overlay(image_rgb: np.ndarray, labels: np.ndarray, alpha: float = 0.35) -> np.ndarray:
    if int(labels.max()) <= 0:
        return image_rgb.copy()

    image_float = image_rgb.astype(np.float32) / 255.0
    rng = np.random.default_rng(42)
    colors = rng.uniform(0.2, 1.0, size=(int(labels.max()) + 1, 3))
    colors[0] = [0, 0, 0]

    color_mask = colors[labels]
    foreground = labels > 0
    overlay = image_float.copy()
    overlay[foreground] = (1 - alpha) * image_float[foreground] + alpha * color_mask[foreground]

    boundaries = segmentation.find_boundaries(labels, mode="outer")
    overlay[boundaries] = [1.0, 1.0, 1.0]
    return np.clip(overlay * 255, 0, 255).astype(np.uint8)
