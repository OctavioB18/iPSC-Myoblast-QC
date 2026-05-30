from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import streamlit as st

from segmentation.cellpose_segmentation import segment_cellpose
from segmentation.opencv_segmentation import segment_opencv


def run_segmentation(image_rgb: np.ndarray, settings: Dict, tr) -> Tuple[np.ndarray, str]:
    if settings["segmentation_method"] == tr("cellpose_advanced"):
        masks = segment_cellpose(
            image_rgb=image_rgb,
            model_type=settings["cellpose_model_type"],
            diameter=settings["cellpose_diameter"],
            use_gpu=settings["cellpose_use_gpu"],
            tr=tr,
        )
        if masks is not None:
            return masks, f"Cellpose-{settings['cellpose_model_type']}"
        st.warning(tr("opencv_fallback"))

    labels = segment_opencv(
        image_rgb=image_rgb,
        blur_kernel=settings["blur_kernel"],
        min_object_area=settings["min_object_area"],
        use_adaptive_threshold=settings["use_adaptive_threshold"],
        invert_threshold=settings["invert_threshold"],
    )
    return labels, "OpenCV"
