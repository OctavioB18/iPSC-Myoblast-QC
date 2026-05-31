from __future__ import annotations
import json, shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from PIL import Image
from models import AutoMetrics, ManualAnnotation
from utils import safe_name


def labels_to_uint16(labels: np.ndarray) -> np.ndarray:
    labels = labels.astype(np.uint32)
    if labels.max() <= 65535:
        return labels.astype(np.uint16)
    return (labels.astype(np.float32) / labels.max() * 65535).astype(np.uint16)


def labels_to_preview_uint8(labels: np.ndarray) -> np.ndarray:
    """Create an 8-bit preview mask for Streamlit/web display.

    The scientific mask is saved as 16-bit TIFF to preserve labels, but
    Streamlit/Pillow may fail when rendering mode I;16 as JPEG. This preview
    is only for visualization: foreground = 255, background = 0.
    """
    return ((labels > 0).astype(np.uint8) * 255)


def save_analysis_assets(analyses_dir: Path, analysis_id: str, image_name: str, image_rgb: np.ndarray,
                         overlay: np.ndarray, labels: np.ndarray) -> dict:
    analysis_dir = analyses_dir / analysis_id
    analysis_dir.mkdir(parents=True, exist_ok=True)
    original_path = analysis_dir / f"{safe_name(Path(image_name).stem)}_original.png"
    overlay_path = analysis_dir / "overlay.png"
    mask_path = analysis_dir / "mask.tif"
    mask_preview_path = analysis_dir / "mask_preview.png"
    Image.fromarray(image_rgb).save(original_path)
    Image.fromarray(overlay).save(overlay_path)
    # Raw labeled mask for downstream analysis.
    Image.fromarray(labels_to_uint16(labels)).save(mask_path)
    # Display-safe preview for Streamlit/GitHub/review screens.
    Image.fromarray(labels_to_preview_uint8(labels)).save(mask_preview_path)
    return {
        "analysis_dir": str(analysis_dir),
        "original_image_path": str(original_path),
        "overlay_path": str(overlay_path),
        "mask_path": str(mask_path),
        "mask_preview_path": str(mask_preview_path),
    }


def save_record(csv_path: Path, json_path: Path, metrics: AutoMetrics, annotation: ManualAnnotation,
                asset_paths: dict, settings: dict) -> pd.DataFrame:
    record = {
        **asdict(metrics),
        **asdict(annotation),
        **asset_paths,
        "opencv_blur_kernel": settings.get("blur_kernel"),
        "opencv_min_object_area": settings.get("min_object_area"),
        "opencv_adaptive_threshold": settings.get("use_adaptive_threshold"),
        "opencv_invert_threshold": settings.get("invert_threshold"),
        "elongated_threshold": settings.get("elongated_threshold"),
        "myotube_area_threshold": settings.get("myotube_area_threshold"),
        "myotube_aspect_ratio_threshold": settings.get("myotube_aspect_ratio_threshold"),
        "software_version": "v4-session-state-analysis-id",
    }
    analysis_dir = Path(asset_paths["analysis_dir"])
    with open(analysis_dir / "record.json", "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    with open(analysis_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
    with open(analysis_dir / "annotation.json", "w", encoding="utf-8") as f:
        json.dump(asdict(annotation), f, indent=2, ensure_ascii=False)

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    return df


def load_records(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame()
    return pd.read_csv(csv_path)
