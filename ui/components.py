from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from models import AutoMetrics, ManualAnnotation
from ui.legend import build_legend


def display_mask_image(mask_path: str, mask_preview_path: str | None = None):
    """Display a mask safely in Streamlit.

    Raw masks are stored as 16-bit TIFF label images for reproducibility.
    Streamlit may attempt to encode PIL mode I;16 as JPEG, which raises:
    "OSError: cannot write mode I;16 as JPEG".

    This function first uses the 8-bit PNG preview when available. If older
    records do not have a preview, it converts the TIFF to an 8-bit binary
    image on the fly before rendering.
    """
    if mask_preview_path and Path(str(mask_preview_path)).exists():
        st.image(Image.open(mask_preview_path).convert("L"), use_container_width=True)
        return

    if mask_path and Path(str(mask_path)).exists():
        mask = Image.open(mask_path)
        arr = np.array(mask)
        preview = ((arr > 0).astype(np.uint8) * 255)
        st.image(preview, use_container_width=True)


def sidebar_settings(tr, lang: str) -> dict:
    st.sidebar.header(tr("settings"))
    input_mode = st.sidebar.radio(tr("input_mode"), [tr("upload_image"), tr("folder_image")], index=0)
    root_dir = st.sidebar.text_input(tr("image_folder"), value="images")
    output_dir = st.sidebar.text_input(tr("output_folder"), value="outputs")
    st.sidebar.divider()
    st.sidebar.subheader(tr("preprocessing"))
    max_side = st.sidebar.slider(tr("max_side"), 512, 4096, 1800, 128)
    st.sidebar.divider()
    st.sidebar.subheader(tr("segmentation_method"))
    segmentation_method = st.sidebar.radio(tr("segmentation_method"), [tr("opencv_fast"), tr("cellpose_advanced")], index=0)
    st.sidebar.subheader(tr("cellpose_settings"))
    cellpose_model_type = st.sidebar.selectbox(tr("cellpose_model"), ["cyto3", "cyto2", "nuclei"], index=0)
    diameter_text = st.sidebar.text_input(tr("cellpose_diameter"), value="")
    cellpose_diameter = None
    if diameter_text.strip():
        try:
            cellpose_diameter = float(diameter_text)
        except ValueError:
            st.sidebar.warning("Invalid diameter. Using automatic estimation.")
    cellpose_use_gpu = st.sidebar.checkbox(tr("cellpose_gpu"), value=False)
    st.sidebar.subheader(tr("opencv_settings"))
    blur_kernel = st.sidebar.slider(tr("blur"), 1, 21, 5, 2)
    min_object_area = st.sidebar.slider(tr("min_area"), 10, 5000, 120, 10)
    use_adaptive_threshold = st.sidebar.checkbox(tr("adaptive_threshold"), value=True)
    invert_threshold = st.sidebar.checkbox(tr("invert_threshold"), value=False)
    st.sidebar.divider()
    st.sidebar.subheader(tr("morphology_criteria"))
    elongated_threshold = st.sidebar.slider(tr("elongated_threshold"), 1.0, 10.0, 3.0, 0.1)
    myotube_area_threshold = st.sidebar.slider(tr("myotube_area_threshold"), 100, 20000, 800, 100)
    myotube_aspect_ratio_threshold = st.sidebar.slider(tr("myotube_ar_threshold"), 1.0, 15.0, 4.0, 0.1)
    overlay_alpha = st.sidebar.slider(tr("overlay_alpha"), 0.05, 0.90, 0.35, 0.05)
    return locals()


def annotation_form(tr, project_or_series: str) -> Optional[ManualAnnotation]:
    st.subheader(tr("annotations"))
    with st.form("annotation_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            researcher = st.text_input(tr("researcher"), value="")
            cell_line = st.text_input(tr("cell_line"), value="")
            differentiation_day = st.number_input(tr("day"), min_value=0, max_value=365, value=0, step=1)
        with c2:
            protocol_name = st.text_input(tr("protocol"), value="")
            medium = st.text_input(tr("medium"), value="")
            supplements_or_factors = st.text_area(tr("supplements"), value="", height=80)
        with c3:
            coating_matrix = st.text_input(tr("coating"), value="Matrigel / Laminin / other")
            passage_number = st.text_input(tr("passage"), value="")
            seeding_density = st.text_input(tr("seeding"), value="")
        c4, c5 = st.columns(2)
        with c4:
            last_medium_change = st.text_input(tr("last_medium_change"), value="")
            expected_stage = st.selectbox(tr("expected_stage"), ["iPSC", "Mesoderm", "Myogenic progenitor", "Myoblast", "Early myotube", "Mature myotube", "Other/undefined"])
            observed_stage = st.selectbox(tr("observed_stage"), ["Consistent with expected", "iPSC-like", "Progenitor", "Myoblast", "Myotube", "High cell death", "Contamination/suspected", "Undefined"])
        with c5:
            markers_tested = st.text_input(tr("markers"), value="PAX7, MYOD1, MYOG, MYHC")
            marker_result_summary = st.text_area(tr("marker_summary"), value="", height=80)
            quality_score = st.slider(tr("quality"), 1, 5, 3)
        c6, c7 = st.columns(2)
        with c6:
            contamination_signs = st.selectbox(tr("contamination"), ["Not observed", "Suspected", "Confirmed", "Not assessed"])
        with c7:
            stress_or_death_signs = st.selectbox(tr("stress"), ["Low", "Moderate", "High", "Not assessed"])
        free_notes = st.text_area(tr("notes"), value="", height=120)
        exclude_from_analysis = st.checkbox(tr("exclude"), value=False)
        submitted = st.form_submit_button(tr("save_annotation"))
    if not submitted:
        return None
    return ManualAnnotation(project_or_series=project_or_series, researcher=researcher, cell_line=cell_line,
        differentiation_day=int(differentiation_day), protocol_name=protocol_name, medium=medium,
        supplements_or_factors=supplements_or_factors, coating_matrix=coating_matrix, passage_number=passage_number,
        seeding_density=seeding_density, last_medium_change=last_medium_change, expected_stage=expected_stage,
        observed_stage=observed_stage, markers_tested=markers_tested, marker_result_summary=marker_result_summary,
        contamination_signs=contamination_signs, stress_or_death_signs=stress_or_death_signs,
        quality_score_1_to_5=int(quality_score), exclude_from_analysis=bool(exclude_from_analysis), free_notes=free_notes)


def biological_interpretation(metrics: AutoMetrics, lang="en") -> list[str]:
    pt = lang == "pt"
    if metrics.object_count == 0:
        return ["Nenhum objeto foi detectado. Ajuste threshold, área mínima ou inverta o threshold." if pt else "No objects were detected. Adjust threshold, minimum area, or invert threshold."]
    out = []
    if metrics.confluence_percent < 20:
        out.append("Baixa confluência: cultura esparsa ou segmentação conservadora." if pt else "Low confluence: sparse culture or conservative segmentation.")
    elif metrics.confluence_percent < 50:
        out.append("Confluência intermediária: compatível com expansão ou início de diferenciação." if pt else "Intermediate confluence: compatible with expansion or early differentiation.")
    elif metrics.confluence_percent < 80:
        out.append("Confluência alta: pode favorecer alinhamento e início de fusão celular." if pt else "High confluence: may favor alignment and early fusion.")
    else:
        out.append("Confluência muito alta: possível cultura densa, fusão avançada ou supersegmentação." if pt else "Very high confluence: dense culture, advanced fusion, or over-segmentation may be present.")
    out.append(("Razão de aspecto média elevada: tendência de morfologia alongada/fusiforme." if pt else "High mean aspect ratio: elongated/spindle-like morphology trend.") if metrics.mean_aspect_ratio >= 3 else ("Razão de aspecto média baixa: objetos mais arredondados ou pouco alongados." if pt else "Low mean aspect ratio: objects are more rounded or weakly elongated."))
    if metrics.myotube_candidate_count > 0:
        out.append("Candidatos a miotubo detectados; confirme com marcadores e/ou análise nuclear." if pt else "Myotube candidates detected; confirm with markers and/or nuclear analysis.")
    else:
        out.append("Nenhum candidato claro a miotubo foi detectado com os limiares atuais." if pt else "No clear myotube candidates detected with current thresholds.")
    return out


def show_metrics(tr, metrics: AutoMetrics, lang="en"):
    st.subheader(tr("metrics"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("confluence"), f"{metrics.confluence_percent:.1f}%")
    c2.metric(tr("objects"), metrics.object_count)
    c3.metric(tr("elongated"), f"{metrics.elongated_object_percent:.1f}%")
    c4.metric(tr("myotube_candidates"), metrics.myotube_candidate_count)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(tr("mean_ar"), f"{metrics.mean_aspect_ratio:.2f}")
    c6.metric(tr("circularity"), f"{metrics.mean_circularity:.2f}")
    c7.metric(tr("mean_area"), f"{metrics.mean_object_area_px:.0f} px")
    c8.metric(tr("time"), f"{metrics.elapsed_seconds:.2f} s")
    st.subheader(tr("bio_interpretation"))
    for item in biological_interpretation(metrics, lang):
        st.info(item)
    metrics_df = pd.DataFrame([asdict(metrics)])
    with st.expander(tr("full_metrics_table"), expanded=True):
        st.dataframe(metrics_df, use_container_width=True)
    with st.expander(tr("legend"), expanded=False):
        st.dataframe(build_legend(metrics_df.columns, lang), use_container_width=True)


def review_previous_analyses(tr, records_df: pd.DataFrame, lang="en"):
    if records_df.empty:
        st.info(tr("no_records"))
        return
    choices = [f"{row.analysis_id} — {row.image_name}" for row in records_df.itertuples()]
    selected = st.selectbox(tr("select_analysis"), choices)
    idx = choices.index(selected)
    row = records_df.iloc[idx]
    st.subheader(f"{tr('analysis_id')}: {row['analysis_id']}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption(tr("original"))
        if Path(row.get("original_image_path", "")).exists():
            st.image(Image.open(row["original_image_path"]), use_container_width=True)
    with c2:
        st.caption(tr("overlay"))
        if Path(row.get("overlay_path", "")).exists():
            st.image(Image.open(row["overlay_path"]), use_container_width=True)
    with c3:
        st.caption(tr("binary_mask"))
        display_mask_image(
            mask_path=str(row.get("mask_path", "")),
            mask_preview_path=str(row.get("mask_preview_path", "")) if "mask_preview_path" in row.index else None,
        )
    st.subheader(tr("metrics"))
    metric_cols = [c for c in records_df.columns if c in build_legend(records_df.columns, lang).iloc[:,0].values]
    st.dataframe(pd.DataFrame([row]), use_container_width=True)
    with st.expander(tr("legend")):
        st.dataframe(build_legend(records_df.columns, lang), use_container_width=True)
