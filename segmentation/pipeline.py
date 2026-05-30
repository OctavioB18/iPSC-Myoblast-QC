
from __future__ import annotations

from typing import Dict, Tuple
import numpy as np
import streamlit as st

from segmentation.opencv_segmentation import segment_opencv
from segmentation.cellpose_segmentation import segment_cellpose

def run_segmentation(image_rgb: np.ndarray, settings: Dict, lang: str = "pt") -> Tuple[np.ndarray, str]:
    wants_cellpose = settings["segmentation_method_key"] == "cellpose"

    if wants_cellpose:
        masks = segment_cellpose(
            image_rgb=image_rgb,
            model_type=settings["cellpose_model_type"],
            diameter=settings["cellpose_diameter"],
            use_gpu=settings["cellpose_use_gpu"],
        )
        if masks is not None:
            return masks, f"Cellpose-{settings['cellpose_model_type']}"

        st.warning("Usando OpenCV como fallback." if lang == "pt" else "Using OpenCV as fallback.")

    labels = segment_opencv(
        image_rgb=image_rgb,
        blur_kernel=settings["blur_kernel"],
        min_object_area=settings["min_object_area"],
        use_adaptive_threshold=settings["use_adaptive_threshold"],
        invert_threshold=settings["invert_threshold"],
    )
    return labels, "OpenCV"
