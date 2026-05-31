from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
from segmentation.opencv_segmentation import opencv_segmentation
from segmentation.cellpose_segmentation import cellpose_segmentation

def run_segmentation(image_rgb: np.ndarray, settings: Dict) -> Tuple[np.ndarray, str]:
    if settings["segmentation_method"] == "Cellpose avançado" or settings["segmentation_method"] == "Advanced Cellpose":
        masks = cellpose_segmentation(
            image_rgb=image_rgb,
            model_type=settings["cellpose_model_type"],
            diameter=settings["cellpose_diameter"],
            use_gpu=settings["cellpose_use_gpu"],
        )
        if masks is not None:
            gpu_text = "GPU" if settings["cellpose_use_gpu"] else "CPU"
            return masks, f"Cellpose-{settings['cellpose_model_type']}-{gpu_text}"
    labels = opencv_segmentation(
        image_rgb=image_rgb,
        blur_kernel=settings["blur_kernel"],
        min_object_area=settings["min_object_area"],
        use_adaptive_threshold=settings["use_adaptive_threshold"],
        invert_threshold=settings["invert_threshold"],
    )
    return labels, "OpenCV-fast"
