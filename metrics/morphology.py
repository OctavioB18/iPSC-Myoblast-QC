from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import List
import numpy as np
from skimage import measure
from models import AutoMetrics

def compute_metrics(labels: np.ndarray, image_name: str, image_path: str, image_sha256: str,
                    analysis_id: str, method: str, settings: dict, elapsed_seconds: float) -> AutoMetrics:
    h, w = labels.shape[:2]
    foreground = labels > 0
    confluence = 100.0 * float(foreground.sum()) / float(h * w)
    props = measure.regionprops(labels)
    areas: List[float] = []
    major_axes: List[float] = []
    minor_axes: List[float] = []
    aspect_ratios: List[float] = []
    circularities: List[float] = []
    elongated_count = 0
    myotube_count = 0
    for p in props:
        area = float(p.area)
        major = float(p.major_axis_length) if p.major_axis_length else 0.0
        minor = float(p.minor_axis_length) if p.minor_axis_length else 0.0
        perimeter = float(p.perimeter) if p.perimeter else 0.0
        aspect_ratio = major / minor if minor > 1e-6 else 0.0
        circularity = 4.0 * np.pi * area / (perimeter ** 2) if perimeter > 1e-6 else 0.0
        areas.append(area); major_axes.append(major); minor_axes.append(minor)
        aspect_ratios.append(aspect_ratio); circularities.append(circularity)
        if aspect_ratio >= settings["elongated_threshold"]:
            elongated_count += 1
        if area >= settings["myotube_area_threshold"] and aspect_ratio >= settings["myotube_aspect_ratio_threshold"]:
            myotube_count += 1
    count = len(props)
    def mean(values): return float(np.mean(values)) if values else 0.0
    def median(values): return float(np.median(values)) if values else 0.0
    return AutoMetrics(
        analysis_id=analysis_id,
        image_name=image_name,
        image_sha256=image_sha256,
        image_path=str(image_path),
        timestamp=datetime.now().isoformat(timespec="seconds"),
        segmentation_method=method,
        segmentation_model=settings.get("cellpose_model_type", ""),
        segmentation_gpu=bool(settings.get("cellpose_use_gpu", False)),
        segmentation_diameter=str(settings.get("cellpose_diameter", "")),
        image_width_px=w,
        image_height_px=h,
        confluence_percent=round(confluence, 3),
        object_count=count,
        mean_object_area_px=round(mean(areas), 3),
        median_object_area_px=round(median(areas), 3),
        mean_major_axis_px=round(mean(major_axes), 3),
        mean_minor_axis_px=round(mean(minor_axes), 3),
        mean_aspect_ratio=round(mean(aspect_ratios), 3),
        median_aspect_ratio=round(median(aspect_ratios), 3),
        mean_circularity=round(mean(circularities), 3),
        elongated_object_count=elongated_count,
        elongated_object_percent=round(100.0 * elongated_count / count, 3) if count else 0.0,
        myotube_candidate_count=myotube_count,
        myotube_candidate_percent=round(100.0 * myotube_count / count, 3) if count else 0.0,
        elapsed_seconds=round(elapsed_seconds, 3),
    )
