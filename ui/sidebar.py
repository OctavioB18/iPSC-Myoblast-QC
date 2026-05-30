
from __future__ import annotations

from typing import Dict
import streamlit as st
from translations import tr, get_lang_code

def language_selector() -> str:
    st.markdown(
        """
        <style>
        div[data-testid="stSelectbox"] label {font-size: 0.85rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns([0.74, 0.26])
    with cols[1]:
        selected = st.selectbox(
            "🌐",
            ["🇧🇷 Português", "🇺🇸 English"],
            index=0,
            key="language_selector",
            label_visibility="collapsed",
        )
    return get_lang_code(selected)

def sidebar_settings(lang: str) -> Dict:
    st.sidebar.header(tr(lang, "settings"))

    input_mode = st.sidebar.radio(
        tr(lang, "input_source"),
        [tr(lang, "upload_image"), tr(lang, "folder_image")],
        index=0,
    )
    input_mode_key = "upload" if input_mode == tr(lang, "upload_image") else "folder"

    folder_dir = st.sidebar.text_input(tr(lang, "folder_label"), value="images")
    output_dir = st.sidebar.text_input(tr(lang, "output_folder"), value="outputs")

    st.sidebar.divider()
    st.sidebar.subheader(tr(lang, "preprocessing"))
    max_side = st.sidebar.slider(tr(lang, "max_side"), 512, 4096, 1800, 128)

    st.sidebar.divider()
    st.sidebar.subheader(tr(lang, "segmentation_method"))
    method_label = st.sidebar.radio(
        tr(lang, "choose_method"),
        [tr(lang, "opencv"), tr(lang, "cellpose")],
        index=0,
    )
    segmentation_method_key = "cellpose" if method_label == tr(lang, "cellpose") else "opencv"

    st.sidebar.subheader(tr(lang, "cellpose_settings"))
    cellpose_model_type = st.sidebar.selectbox(tr(lang, "cellpose_model"), ["cyto3", "cyto2", "nuclei"], index=0)
    diameter_text = st.sidebar.text_input(tr(lang, "cellpose_diameter"), value="")
    cellpose_diameter = None
    if diameter_text.strip():
        try:
            cellpose_diameter = float(diameter_text)
        except ValueError:
            st.sidebar.warning("Diâmetro inválido. Usando automático." if lang == "pt" else "Invalid diameter. Using automatic.")
    cellpose_use_gpu = st.sidebar.checkbox(tr(lang, "cellpose_gpu"), value=False)

    st.sidebar.subheader(tr(lang, "opencv_settings"))
    blur_kernel = st.sidebar.slider(tr(lang, "blur"), 1, 21, 5, 2)
    min_object_area = st.sidebar.slider(tr(lang, "min_area"), 10, 5000, 120, 10)
    use_adaptive_threshold = st.sidebar.checkbox(tr(lang, "adaptive"), value=True)
    invert_threshold = st.sidebar.checkbox(tr(lang, "invert"), value=False)

    st.sidebar.divider()
    st.sidebar.subheader(tr(lang, "morphology"))
    elongated_threshold = st.sidebar.slider(tr(lang, "elongated_threshold"), 1.0, 10.0, 3.0, 0.1)
    myotube_area_threshold = st.sidebar.slider(tr(lang, "myotube_area"), 100, 20000, 800, 100)
    myotube_aspect_ratio_threshold = st.sidebar.slider(tr(lang, "myotube_ar"), 1.0, 15.0, 4.0, 0.1)
    overlay_alpha = st.sidebar.slider(tr(lang, "overlay_alpha"), 0.05, 0.90, 0.35, 0.05)

    return {
        "input_mode_key": input_mode_key,
        "folder_dir": folder_dir,
        "output_dir": output_dir,
        "max_side": max_side,
        "segmentation_method_key": segmentation_method_key,
        "cellpose_model_type": cellpose_model_type,
        "cellpose_diameter": cellpose_diameter,
        "cellpose_use_gpu": cellpose_use_gpu,
        "blur_kernel": blur_kernel,
        "min_object_area": min_object_area,
        "use_adaptive_threshold": use_adaptive_threshold,
        "invert_threshold": invert_threshold,
        "elongated_threshold": elongated_threshold,
        "myotube_area_threshold": myotube_area_threshold,
        "myotube_aspect_ratio_threshold": myotube_aspect_ratio_threshold,
        "overlay_alpha": overlay_alpha,
    }
