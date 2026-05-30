from __future__ import annotations

import streamlit as st

from config import DEFAULT_IMAGE_DIR, DEFAULT_OUTPUT_DIR
from translations import get_language_code, make_translator


def language_selector():
    top_left, top_right = st.columns([5, 1])
    with top_right:
        language_label = st.selectbox(
            "🌐",
            ["🇧🇷 Português", "🇺🇸 English"],
            index=0,
            label_visibility="collapsed",
        )
    lang = get_language_code(language_label)
    tr = make_translator(lang)
    return lang, tr


def sidebar_settings(tr):
    st.sidebar.header(tr("settings"))

    image_source = st.sidebar.radio(
        tr("image_source"),
        [tr("upload_image"), tr("use_folder")],
        index=0,
    )

    root_dir = st.sidebar.text_input(tr("folder_path"), value=DEFAULT_IMAGE_DIR)
    output_dir = st.sidebar.text_input(tr("output_folder"), value=DEFAULT_OUTPUT_DIR)

    st.sidebar.divider()
    st.sidebar.subheader(tr("preprocessing"))
    max_side = st.sidebar.slider(tr("max_side"), 512, 4096, 1800, 128)

    st.sidebar.divider()
    st.sidebar.subheader(tr("segmentation_method"))
    segmentation_method = st.sidebar.radio(
        tr("segmentation_method"),
        [tr("opencv_fast"), tr("cellpose_advanced")],
        index=0,
    )

    st.sidebar.subheader(tr("cellpose"))
    cellpose_model_type = st.sidebar.selectbox(tr("cellpose_model"), ["cyto3", "cyto2", "nuclei"], index=0)
    diameter_text = st.sidebar.text_input(tr("cellpose_diameter"), value="")
    cellpose_diameter = None
    if diameter_text.strip():
        try:
            cellpose_diameter = float(diameter_text)
        except ValueError:
            st.sidebar.warning("Invalid diameter. Using automatic estimation.")
    cellpose_use_gpu = st.sidebar.checkbox(tr("cellpose_gpu"), value=False)

    st.sidebar.subheader(tr("opencv"))
    blur_kernel = st.sidebar.slider(tr("blur"), 1, 21, 5, 2)
    min_object_area = st.sidebar.slider(tr("min_area"), 10, 5000, 120, 10)
    use_adaptive_threshold = st.sidebar.checkbox(tr("adaptive_threshold"), value=True)
    invert_threshold = st.sidebar.checkbox(tr("invert_threshold"), value=False)

    st.sidebar.divider()
    st.sidebar.subheader(tr("morphology"))
    elongated_threshold = st.sidebar.slider(tr("elongated_threshold"), 1.0, 10.0, 3.0, 0.1)
    myotube_area_threshold = st.sidebar.slider(tr("myotube_area"), 100, 20000, 800, 100)
    myotube_aspect_ratio_threshold = st.sidebar.slider(tr("myotube_aspect"), 1.0, 15.0, 4.0, 0.1)
    overlay_alpha = st.sidebar.slider(tr("overlay_alpha"), 0.05, 0.90, 0.35, 0.05)

    return {
        "image_source": image_source,
        "root_dir": root_dir,
        "output_dir": output_dir,
        "max_side": max_side,
        "segmentation_method": segmentation_method,
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
