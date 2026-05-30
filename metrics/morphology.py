from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np
from skimage import measure

from models import AutoMetrics


def compute_metrics(
    labels: np.ndarray,
    image_path: str,
    image_name: str,
    method: str,
    elongated_threshold: float,
    myotube_area_threshold: int,
    myotube_aspect_ratio_threshold: float,
) -> AutoMetrics:
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

        areas.append(area)
        major_axes.append(major)
        minor_axes.append(minor)
        aspect_ratios.append(aspect_ratio)
        circularities.append(circularity)

        if aspect_ratio >= elongated_threshold:
            elongated_count += 1
        if area >= myotube_area_threshold and aspect_ratio >= myotube_aspect_ratio_threshold:
            myotube_count += 1

    count = len(props)

    def mean_or_zero(values: List[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    def median_or_zero(values: List[float]) -> float:
        return float(np.median(values)) if values else 0.0

    return AutoMetrics(
        image_name=image_name or Path(image_path).name,
        image_path=image_path,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        segmentation_method=method,
        image_width_px=w,
        image_height_px=h,
        confluence_percent=round(confluence, 3),
        object_count=count,
        mean_object_area_px=round(mean_or_zero(areas), 3),
        median_object_area_px=round(median_or_zero(areas), 3),
        mean_major_axis_px=round(mean_or_zero(major_axes), 3),
        mean_minor_axis_px=round(mean_or_zero(minor_axes), 3),
        mean_aspect_ratio=round(mean_or_zero(aspect_ratios), 3),
        median_aspect_ratio=round(median_or_zero(aspect_ratios), 3),
        mean_circularity=round(mean_or_zero(circularities), 3),
        elongated_object_count=elongated_count,
        elongated_object_percent=round(100.0 * elongated_count / count, 3) if count else 0.0,
        myotube_candidate_count=myotube_count,
        myotube_candidate_percent=round(100.0 * myotube_count / count, 3) if count else 0.0,
    )
