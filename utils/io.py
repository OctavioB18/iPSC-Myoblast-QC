
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
from PIL import Image
import numpy as np

from utils.images import safe_name, labels_to_uint16

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

def save_images(overlays_dir: Path, masks_dir: Path, image_name: str, overlay: np.ndarray, labels: np.ndarray) -> Tuple[Path, Path]:
    from datetime import datetime
    stem = safe_name(Path(image_name).stem)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    overlay_path = overlays_dir / f"{stem}_overlay_{timestamp}.png"
    mask_path = masks_dir / f"{stem}_mask_{timestamp}.tif"
    Image.fromarray(overlay).save(overlay_path)
    Image.fromarray(labels_to_uint16(labels)).save(mask_path)
    return overlay_path, mask_path

def save_record(csv_path: Path, json_path: Path, annotation, metrics) -> pd.DataFrame:
    row = {**asdict(annotation), **asdict(metrics)}
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    # Avoid exporting pandas index as "Unnamed: 0"
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    return df
