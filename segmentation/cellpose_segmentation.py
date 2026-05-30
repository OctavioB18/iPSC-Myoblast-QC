
from __future__ import annotations

from typing import Optional
import numpy as np
import streamlit as st

def segment_cellpose(
    image_rgb: np.ndarray,
    model_type: str = "cyto3",
    diameter: Optional[float] = None,
    use_gpu: bool = False,
) -> Optional[np.ndarray]:
    try:
        from cellpose import models
    except Exception as exc:
        st.error(f"Cellpose could not be imported: {exc}")
        return None

    try:
        model = models.CellposeModel(gpu=use_gpu, model_type=model_type)
        masks, flows, styles = model.eval(
            image_rgb,
            diameter=diameter,
            channels=[0, 0],
        )
        masks = masks.astype(np.int32)
        if masks.max() <= 0:
            st.warning("Cellpose ran but detected no objects.")
            return None
        return masks
    except Exception as exc:
        st.error(f"Cellpose failed during segmentation: {exc}")
        return None
