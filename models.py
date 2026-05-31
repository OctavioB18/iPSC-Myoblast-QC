from __future__ import annotations
from dataclasses import dataclass

@dataclass
class AutoMetrics:
    analysis_id: str
    image_name: str
    image_sha256: str
    image_path: str
    timestamp: str
    segmentation_method: str
    segmentation_model: str
    segmentation_gpu: bool
    segmentation_diameter: str
    image_width_px: int
    image_height_px: int
    confluence_percent: float
    object_count: int
    mean_object_area_px: float
    median_object_area_px: float
    mean_major_axis_px: float
    mean_minor_axis_px: float
    mean_aspect_ratio: float
    median_aspect_ratio: float
    mean_circularity: float
    elongated_object_count: int
    elongated_object_percent: float
    myotube_candidate_count: int
    myotube_candidate_percent: float
    elapsed_seconds: float

@dataclass
class ManualAnnotation:
    project_or_series: str
    researcher: str
    cell_line: str
    differentiation_day: int
    protocol_name: str
    medium: str
    supplements_or_factors: str
    coating_matrix: str
    passage_number: str
    seeding_density: str
    last_medium_change: str
    expected_stage: str
    observed_stage: str
    markers_tested: str
    marker_result_summary: str
    contamination_signs: str
    stress_or_death_signs: str
    quality_score_1_to_5: int
    exclude_from_analysis: bool
    free_notes: str
