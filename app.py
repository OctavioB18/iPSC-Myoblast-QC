
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import streamlit as st

from metrics.morphology import compute_metrics
from segmentation.pipeline import run_segmentation
from translations import tr
from ui.annotations import annotation_form
from ui.metrics_display import show_metrics, show_saved_records
from ui.sidebar import language_selector, sidebar_settings
from ui.visualization import create_overlay
from utils.images import (
    SUPPORTED_EXTENSIONS,
    list_images,
    load_image_from_path,
    load_image_from_upload,
    resize_if_large,
)
from utils.io import ensure_output_dirs, save_images, save_record


def main():
    st.set_page_config(page_title="iPSC-Myoblast Image QC & Annotation", layout="wide")

    lang = language_selector()

    st.title(tr(lang, "app_title"))
    st.write(tr(lang, "app_subtitle"))

    settings = sidebar_settings(lang)

    project_or_series = st.text_input(
        tr(lang, "project_name"),
        value="myoblast_experiment",
    )
    output_dirs = ensure_output_dirs(settings["output_dir"], project_or_series)

    image_rgb_original = None
    image_name = None
    image_source_text = None

    if settings["input_mode_key"] == "upload":
        uploaded = st.file_uploader(
            tr(lang, "upload_label"),
            type=[ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS],
        )
        if uploaded is None:
            st.info("Carregue uma imagem para iniciar." if lang == "pt" else "Upload an image to start.")
            st.stop()
        image_rgb_original = load_image_from_upload(uploaded)
        image_name = uploaded.name
        image_source_text = f"arquivo carregado: {uploaded.name}" if lang == "pt" else f"uploaded file: {uploaded.name}"

    else:
        images = list_images(settings["folder_dir"])
        if not images:
            st.error(tr(lang, "no_images"))
            st.stop()

        root_resolved = Path(settings["folder_dir"]).expanduser().resolve()
        image_labels = []
        for p in images:
            try:
                image_labels.append(str(Path(p).relative_to(root_resolved)))
            except ValueError:
                image_labels.append(Path(p).name)

        selected_label = st.selectbox(tr(lang, "choose_image"), image_labels)
        selected_path = images[image_labels.index(selected_label)]
        image_rgb_original = load_image_from_path(selected_path)
        image_name = Path(selected_path).name
        image_source_text = selected_path

    image_rgb = resize_if_large(image_rgb_original, settings["max_side"])

    st.caption(f"{tr(lang, 'selected_image')}: {image_name}")
    if image_rgb.shape != image_rgb_original.shape:
        st.caption(
            f"{tr(lang, 'resized')}: {image_rgb.shape[1]} × {image_rgb.shape[0]} px; "
            f"original: {image_rgb_original.shape[1]} × {image_rgb_original.shape[0]} px."
        )

    with st.spinner(tr(lang, "segmenting")):
        t0 = time.time()
        labels, method_used = run_segmentation(image_rgb, settings, lang)
        overlay = create_overlay(image_rgb, labels, alpha=settings["overlay_alpha"])
        metrics = compute_metrics(
            labels=labels,
            image_name=image_name,
            image_path=image_source_text,
            method=method_used,
            elongated_threshold=settings["elongated_threshold"],
            myotube_area_threshold=settings["myotube_area_threshold"],
            myotube_aspect_ratio_threshold=settings["myotube_aspect_ratio_threshold"],
        )
        elapsed_seconds = time.time() - t0

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            tr(lang, "tab_image"),
            tr(lang, "tab_metrics"),
            tr(lang, "tab_annotation"),
            tr(lang, "tab_records"),
        ]
    )

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(tr(lang, "original"))
            st.image(image_rgb, use_container_width=True)
        with c2:
            st.subheader(f"{tr(lang, 'overlay')} — {method_used}")
            st.image(overlay, use_container_width=True)

        with st.expander(tr(lang, "binary_mask")):
            st.image(labels > 0, caption=tr(lang, "binary_mask"), use_container_width=True)

        if st.button(tr(lang, "save_overlay")):
            overlay_path, mask_path = save_images(
                output_dirs["overlays"],
                output_dirs["masks"],
                image_name,
                overlay,
                labels,
            )
            st.success(f"{tr(lang, 'overlay_saved')}: {overlay_path}")
            st.success(f"{tr(lang, 'mask_saved')}: {mask_path}")

    with tab2:
        show_metrics(metrics, elapsed_seconds, lang)
        st.warning(tr(lang, "warning_metrics"))

    with tab3:
        annotation = annotation_form(lang, project_or_series, image_name)
        if annotation is not None:
            overlay_path, mask_path = save_images(
                output_dirs["overlays"],
                output_dirs["masks"],
                image_name,
                overlay,
                labels,
            )
            df = save_record(output_dirs["csv"], output_dirs["json"], annotation, metrics)
            st.success(tr(lang, "saved_success"))
            st.write(f"CSV: `{output_dirs['csv']}`")
            st.write(f"JSON: `{output_dirs['json']}`")
            st.write(f"Overlay: `{overlay_path}`")
            st.write(f"Mask: `{mask_path}`")
            st.dataframe(df.tail(5), use_container_width=True)

    with tab4:
        show_saved_records(output_dirs["csv"], lang)


if __name__ == "__main__":
    main()
