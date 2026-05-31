from __future__ import annotations
import hashlib, re, uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import numpy as np
from PIL import Image
import streamlit as st
import cv2

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
DEFAULT_OUTPUT_DIR = "outputs"

def safe_name(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^a-zA-Z0-9_\-.]", "", text)
    return text or "unnamed"

def make_analysis_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

@st.cache_data(show_spinner=False)
def list_images(root_dir: str) -> List[str]:
    root = Path(root_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return []
    return [str(p) for p in sorted(root.rglob("*")) if p.suffix.lower() in SUPPORTED_EXTENSIONS]

@st.cache_data(show_spinner=False)
def load_image_from_path(path: str) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))

def load_image_from_upload(uploaded_file) -> tuple[np.ndarray, bytes]:
    data = uploaded_file.getvalue()
    img = Image.open(uploaded_file).convert("RGB")
    return np.array(img), data

def ensure_output_dirs(output_root: str, project_or_series: str) -> Dict[str, Path]:
    root = Path(output_root).expanduser().resolve()
    project_dir = root / safe_name(project_or_series)
    analyses_dir = project_dir / "analyses"
    tables_dir = project_dir / "tables"
    for folder in [project_dir, analyses_dir, tables_dir]:
        folder.mkdir(parents=True, exist_ok=True)
    return {"project": project_dir, "analyses": analyses_dir, "tables": tables_dir,
            "csv": tables_dir / "records.csv", "json": tables_dir / "records.json"}

def normalize_to_uint8(gray: np.ndarray) -> np.ndarray:
    gray = gray.astype(np.float32)
    mn, mx = float(gray.min()), float(gray.max())
    if mx - mn < 1e-6:
        return np.zeros_like(gray, dtype=np.uint8)
    return ((gray - mn) / (mx - mn) * 255).astype(np.uint8)

def resize_if_large(image_rgb: np.ndarray, max_side: int) -> np.ndarray:
    h, w = image_rgb.shape[:2]
    if max(h, w) <= max_side:
        return image_rgb
    scale = max_side / max(h, w)
    return cv2.resize(image_rgb, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
