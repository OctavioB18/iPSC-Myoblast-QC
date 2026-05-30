from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from config import APP_TITLE, SUPPORTED_EXTENSIONS
from metrics.morphology import compute_metrics
from segmentation.pipeline import run_segmentation
from ui.annotations import annotation_form
from ui.dashboard import show_metrics, show_saved_records
from ui.sidebar import language_selector, sidebar_settings
from ui.visualization import create_overlay
from utils.image_ops import resize_if_large
from utils.io import (
    ensure_output_dirs,
    list_images,
    load_image_from_path,
    load_image_from_upload,
    save_images,
    save_record,
)


def choose_image(settings, tr):
    if settings["image_source"] == tr("upload_image"):
        uploaded_file = st.file_uploader(
            tr("upload_label"),
            type=[ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS],
        )
        if uploaded_file is None:
            st.stop()
        image_rgb = load_image_from_upload(uploaded_file)
        image_name = uploaded_file.name
        image_path_display = f"{tr('uploaded_file')}: {uploaded_file.name}"
        return image_rgb, image_name, image_path_display

    images = list_images(settings["root_dir"])
    if not images:
        st.error(tr("no_images"))
        st.stop()

    st.sidebar.success(f"{len(images)} image(s)")
    root_resolved = Path(settings["root_dir"]).expanduser().resolve()
    labels = []
    for p in images:
        try:
            labels.append(str(Path(p).relative_to(root_resolved)))
        except ValueError:
            labels.append(Path(p).name)

    selected_label = st.selectbox(tr("choose_image"), labels)
    selected_path = images[labels.index(selected_label)]
    image_rgb = load_image_from_path(selected_path)
    image_name = Path(selected_path).name
    return image_rgb, image_name, selected_path


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    lang, tr = language_selector()
    st.title(tr("app_title"))
    st.write(tr("subtitle"))

    settings = sidebar_settings(tr)

    image_rgb_original, image_name, image_path_display = choose_image(settings, tr)

    project_or_series = st.text_input(
        tr("project_name"),
        value="myoblast_project",
    )

    output_dirs = ensure_output_dirs(settings["output_dir"], project_or_series)
    image_rgb = resize_if_large(image_rgb_original, settings["max_side"])

    st.caption(f"{tr('selected_image')}: {image_path_display}")

    if image_rgb.shape != image_rgb_original.shape:
        st.caption(
            f"{tr('resized')}: {image_rgb.shape[1]} × {image_rgb.shape[0]} px; "
            f"{tr('original_size')}: {image_rgb_original.shape[1]} × {image_rgb_original.shape[0]} px."
        )

    with st.spinner(tr("segmenting")):
        t0 = time.time()
        labels, method_used = run_segmentation(image_rgb, settings, tr)
        overlay = create_overlay(image_rgb, labels, alpha=settings["overlay_alpha"])
        metrics = compute_metrics(
            labels=labels,
            image_path=image_path_display,
            image_name=image_name,
            method=method_used,
            elongated_threshold=settings["elongated_threshold"],
            myotube_area_threshold=settings["myotube_area_threshold"],
            myotube_aspect_ratio_threshold=settings["myotube_aspect_ratio_threshold"],
        )
        elapsed_seconds = time.time() - t0

    tab1, tab2, tab3, tab4 = st.tabs([
        tr("tab_image"),
        tr("tab_metrics"),
        tr("tab_annotate"),
        tr("tab_records"),
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(tr("original"))
            st.image(image_rgb, use_container_width=True)
        with c2:
            st.subheader(f"{tr('overlay')} — {method_used}")
            st.image(overlay, use_container_width=True)

        with st.expander(tr("binary_mask")):
            st.image(labels > 0, caption="Mask", use_container_width=True)

        if st.button(tr("save_overlay")):
            overlay_path, mask_path = save_images(
                output_dirs["overlays"],
                output_dirs["masks"],
                image_name,
                overlay,
                labels,
            )
            st.success(f"{tr('saved_overlay')}: {overlay_path}")
            st.success(f"{tr('saved_mask')}: {mask_path}")

    with tab2:
        show_metrics(metrics, elapsed_seconds, lang, tr)
        st.warning(tr("warning_metrics"))

    with tab3:
        annotation = annotation_form(project_or_series, image_name, tr)
        if annotation is not None:
            overlay_path, mask_path = save_images(
                output_dirs["overlays"],
                output_dirs["masks"],
                image_name,
                overlay,
                labels,
            )
            df = save_record(output_dirs["csv"], output_dirs["json"], annotation, metrics)
            st.success(tr("record_saved"))
            st.write(f"CSV: `{output_dirs['csv']}`")
            st.write(f"JSON: `{output_dirs['json']}`")
            st.write(f"Overlay: `{overlay_path}`")
            st.write(f"Mask: `{mask_path}`")
            st.dataframe(df.tail(5), use_container_width=True)

    with tab4:
        show_saved_records(output_dirs["csv"], tr)


if __name__ == "__main__":
    main()
