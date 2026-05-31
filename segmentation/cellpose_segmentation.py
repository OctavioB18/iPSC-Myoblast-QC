from __future__ import annotations
from typing import Optional
import numpy as np
import streamlit as st

@st.cache_resource(show_spinner=False)
def load_cellpose_model(model_type: str, use_gpu: bool):
    from cellpose import models
    return models.CellposeModel(gpu=use_gpu, model_type=model_type)

def cellpose_segmentation(image_rgb: np.ndarray, model_type: str, diameter: Optional[float], use_gpu: bool) -> Optional[np.ndarray]:
    try:
        model = load_cellpose_model(model_type, use_gpu)
    except Exception as exc:
        st.error(f"Cellpose could not be loaded: {exc}")
        return None
    try:
        masks, flows, styles = model.eval(image_rgb, diameter=diameter, channels=[0, 0])
        masks = masks.astype(np.int32)
        if masks.max() <= 0:
            st.warning("Cellpose ran but did not detect objects.")
            return None
        return masks
    except Exception as exc:
        st.error(f"Cellpose failed during segmentation: {exc}")
        return None
