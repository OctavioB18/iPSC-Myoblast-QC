from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

from config import SUPPORTED_EXTENSIONS
from models import AutoMetrics, ManualAnnotation


def safe_name(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^a-zA-Z0-9_\-.]", "", text)
    return text or "unnamed"


@st.cache_data(show_spinner=False)
def list_images(root_dir: str) -> List[str]:
    root = Path(root_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return []
    return [
        str(p)
        for p in sorted(root.rglob("*"))
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


@st.cache_data(show_spinner=False)
def load_image_from_path(path: str) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def load_image_from_upload(uploaded_file) -> np.ndarray:
    return np.array(Image.open(uploaded_file).convert("RGB"))


def ensure_output_dirs(output_root: str, project_or_series: str) -> Dict[str, Path]:
    root = Path(output_root).expanduser().resolve()
    project_dir = root / safe_name(project_or_series)
    overlays_dir = project_dir / "overlays"
    masks_dir = project_dir / "masks"
    tables_dir = project_dir / "tables"

    for folder in [project_dir, overlays_dir, masks_dir, tables_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    return {
        "project": project_dir,
        "overlays": overlays_dir,
        "masks": masks_dir,
        "tables": tables_dir,
        "csv": tables_dir / "annotations_and_metrics.csv",
        "json": tables_dir / "annotations_and_metrics.json",
    }


def labels_to_uint16(labels: np.ndarray) -> np.ndarray:
    labels = labels.astype(np.uint32)
    if labels.max() <= 65535:
        return labels.astype(np.uint16)
    return (labels.astype(np.float32) / labels.max() * 65535).astype(np.uint16)


def save_images(overlays_dir: Path, masks_dir: Path, image_name: str, overlay: np.ndarray, labels: np.ndarray):
    from datetime import datetime

    stem = safe_name(Path(image_name).stem)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    overlay_path = overlays_dir / f"{stem}_overlay_{timestamp}.png"
    mask_path = masks_dir / f"{stem}_mask_{timestamp}.tif"

    Image.fromarray(overlay).save(overlay_path)
    Image.fromarray(labels_to_uint16(labels)).save(mask_path)

    return overlay_path, mask_path


def save_record(csv_path: Path, json_path: Path, annotation: ManualAnnotation, metrics: AutoMetrics) -> pd.DataFrame:
    row = {**asdict(annotation), **asdict(metrics)}
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    return df
