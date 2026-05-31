from __future__ import annotations
import pandas as pd

COLUMN_DESCRIPTIONS = {
    "analysis_id": ("Unique analysis identifier.", "Connects original image, mask, overlay, metrics, and annotations."),
    "image_name": ("Analyzed image file name.", "Identifies the source image."),
    "image_sha256": ("SHA-256 hash of the image content.", "Helps verify that the same image was used."),
    "image_path": ("Original image path or uploaded file name.", "Useful for traceability."),
    "timestamp": ("Analysis timestamp.", "Supports audit and chronological tracking."),
    "segmentation_method": ("Segmentation method used.", "Records whether OpenCV or Cellpose was used, including GPU/CPU when relevant."),
    "segmentation_model": ("Cellpose model selected.", "Relevant for reproducibility when Cellpose is used."),
    "segmentation_gpu": ("Whether GPU was enabled.", "Important for performance/reproducibility."),
    "segmentation_diameter": ("Cellpose diameter parameter.", "Empty/None means automatic estimation."),
    "image_width_px": ("Analyzed image width in pixels.", "Useful when comparing resized images."),
    "image_height_px": ("Analyzed image height in pixels.", "Useful when comparing resized images."),
    "confluence_percent": ("Percentage of image area segmented as cellular/object area.", "Higher values suggest higher confluence or denser culture."),
    "object_count": ("Number of segmented objects.", "May represent cells, fragments, clusters, or myotube-like objects."),
    "mean_object_area_px": ("Mean segmented object area in pixels.", "Increases with larger cells, clusters, or myotubes."),
    "median_object_area_px": ("Median segmented object area in pixels.", "Less sensitive to outliers than the mean."),
    "mean_major_axis_px": ("Mean major-axis length.", "Increases with elongated cells/myotube-like structures."),
    "mean_minor_axis_px": ("Mean minor-axis length.", "Relates to object width/thickness."),
    "mean_aspect_ratio": ("Mean length/width ratio.", "Higher values indicate elongated or spindle-like morphology."),
    "median_aspect_ratio": ("Median length/width ratio.", "Robust summary of elongation."),
    "mean_circularity": ("Mean object circularity.", "Near 1 is rounder; lower values are more elongated/irregular."),
    "elongated_object_count": ("Number of objects above the elongation threshold.", "May indicate myogenic alignment or elongated artifacts."),
    "elongated_object_percent": ("Percentage of elongated objects.", "Useful for comparing morphology across days/conditions."),
    "myotube_candidate_count": ("Number of large elongated objects classified as myotube candidates.", "Exploratory estimate; validate with markers/nuclei."),
    "myotube_candidate_percent": ("Percentage of myotube candidates.", "May suggest fusion/maturation trends."),
    "elapsed_seconds": ("Segmentation + metrics runtime.", "Helps compare OpenCV/Cellpose performance."),
    "project_or_series": ("Project, series, or experiment name.", "Groups records into experiments."),
    "researcher": ("Researcher/operator.", "Traceability of manual annotation."),
    "cell_line": ("iPSC line.", "Supports comparison across cell lines."),
    "differentiation_day": ("Differentiation day.", "Critical for time-course analysis."),
    "protocol_name": ("Protocol name.", "Supports protocol comparisons."),
    "medium": ("Culture medium.", "Links morphology to culture conditions."),
    "supplements_or_factors": ("Supplements/factors used.", "Records small molecules/growth factors."),
    "coating_matrix": ("Coating matrix.", "May influence adhesion, alignment, and fusion."),
    "passage_number": ("Passage number.", "Can affect cell behavior."),
    "seeding_density": ("Seeding density.", "Strongly affects confluence/fusion."),
    "last_medium_change": ("Last medium change.", "Helps interpret stress/death."),
    "expected_stage": ("Expected stage.", "Allows expected vs observed comparison."),
    "observed_stage": ("Observed stage.", "Human interpretation of morphology."),
    "markers_tested": ("Markers tested.", "Examples: PAX7, MYOD1, MYOG, MYHC."),
    "marker_result_summary": ("Marker result summary.", "Links morphology with biological identity."),
    "contamination_signs": ("Contamination assessment.", "Flags problematic images/cultures."),
    "stress_or_death_signs": ("Stress/death assessment.", "Context for poor morphology or low quality."),
    "quality_score_1_to_5": ("Subjective quality score.", "Quick triage score from 1 to 5."),
    "exclude_from_analysis": ("Whether to exclude from consolidated analysis.", "Keeps the record while allowing filtering."),
    "free_notes": ("Free-text notes.", "Captures details not represented elsewhere."),
    "analysis_dir": ("Folder containing files for this analysis.", "Holds original image, mask, overlay, JSON files."),
    "original_image_path": ("Saved copy of analyzed original image.", "Image used for this exact analysis."),
    "overlay_path": ("Saved overlay path.", "Visualization of segmentation on the image."),
    "mask_path": ("Saved mask path.", "Binary/labeled segmentation mask."),
}

PT_OVERRIDES = {
    "analysis_id": ("Identificador único da análise.", "Conecta imagem original, máscara, overlay, métricas e anotações."),
    "image_name": ("Nome do arquivo analisado.", "Identifica a imagem de origem."),
    "image_sha256": ("Hash SHA-256 da imagem.", "Ajuda a verificar que a mesma imagem foi usada."),
    "segmentation_method": ("Método de segmentação usado.", "Registra OpenCV ou Cellpose, incluindo GPU/CPU quando relevante."),
    "confluence_percent": ("Percentual da área segmentada como célula/objeto.", "Valor maior sugere maior confluência/densidade."),
    "object_count": ("Número de objetos segmentados.", "Pode representar células, fragmentos, grupos ou miotubos."),
    "mean_aspect_ratio": ("Razão média comprimento/largura.", "Valores maiores indicam morfologia alongada/fusiforme."),
    "myotube_candidate_count": ("Número de candidatos a miotubo.", "Estimativa exploratória; valide com marcadores/núcleos."),
    "original_image_path": ("Cópia salva da imagem original analisada.", "Imagem usada nesta análise exata."),
    "overlay_path": ("Caminho do overlay salvo.", "Visualização da segmentação sobre a imagem."),
    "mask_path": ("Caminho da máscara salva.", "Máscara de segmentação binária/rotulada."),
}

def build_legend(columns, lang="en") -> pd.DataFrame:
    rows = []
    for col in columns:
        desc, interp = COLUMN_DESCRIPTIONS.get(col, ("No description available.", "This column was generated by the current software version or user data."))
        if lang == "pt" and col in PT_OVERRIDES:
            desc, interp = PT_OVERRIDES[col]
        rows.append({"Column" if lang == "en" else "Coluna": col,
                     "Description" if lang == "en" else "Significado": desc,
                     "Practical interpretation" if lang == "en" else "Interpretação prática": interp})
    return pd.DataFrame(rows)
