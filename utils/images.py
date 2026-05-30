
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image
import streamlit as st

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

def safe_name(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^a-zA-Z0-9_\-.]", "", text)
    return text or "unnamed"

@st.cache_data(show_spinner=False)
def list_images(root_dir: str) -> List[str]:
    root = Path(root_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return []
    return [str(p) for p in sorted(root.rglob("*")) if p.suffix.lower() in SUPPORTED_EXTENSIONS]

def load_image_from_path(path: str) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))

def load_image_from_upload(uploaded_file) -> np.ndarray:
    return np.array(Image.open(uploaded_file).convert("RGB"))

def resize_if_large(image_rgb: np.ndarray, max_side: int) -> np.ndarray:
    h, w = image_rgb.shape[:2]
    if max(h, w) <= max_side:
        return image_rgb
    scale = max_side / max(h, w)
    return cv2.resize(image_rgb, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

def labels_to_uint16(labels: np.ndarray) -> np.ndarray:
    labels = labels.astype(np.uint32)
    if labels.max() <= 65535:
        return labels.astype(np.uint16)
    return (labels.astype(np.float32) / labels.max() * 65535).astype(np.uint16)
