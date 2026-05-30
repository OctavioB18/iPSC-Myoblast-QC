from __future__ import annotations

from typing import Optional

import numpy as np
import streamlit as st


def segment_cellpose(
    image_rgb: np.ndarray,
    model_type: str,
    diameter: Optional[float],
    use_gpu: bool,
    tr,
) -> Optional[np.ndarray]:
    try:
        from cellpose import models
    except Exception as exc:
        st.error(f"{tr('cellpose_missing')}: {exc}")
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
            st.warning(tr("cellpose_no_objects"))
            return None
        return masks
    except Exception as exc:
        st.error(f"{tr('cellpose_failed')}: {exc}")
        return None
