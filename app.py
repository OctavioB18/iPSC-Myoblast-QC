from __future__ import annotations
import time
from dataclasses import asdict
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from skimage import segmentation

from translations import get_language_code, make_translator
from utils import (DEFAULT_OUTPUT_DIR, ensure_output_dirs, list_images, load_image_from_path,
                   load_image_from_upload, make_analysis_id, resize_if_large, sha256_bytes, sha256_file)
from segmentation.pipeline import run_segmentation
from metrics.morphology import compute_metrics
from data.storage import save_analysis_assets, save_record, load_records
from ui.components import sidebar_settings, annotation_form, show_metrics, review_previous_analyses


def create_overlay(image_rgb: np.ndarray, labels: np.ndarray, alpha: float) -> np.ndarray:
    if int(labels.max()) <= 0:
        return image_rgb.copy()
    image_float = image_rgb.astype(np.float32) / 255.0
    rng = np.random.default_rng(42)
    colors = rng.uniform(0.2, 1.0, size=(int(labels.max()) + 1, 3))
    colors[0] = [0, 0, 0]
    color_mask = colors[labels]
    foreground = labels > 0
    overlay = image_float.copy()
    overlay[foreground] = (1 - alpha) * image_float[foreground] + alpha * color_mask[foreground]
    boundaries = segmentation.find_boundaries(labels, mode="outer")
    overlay[boundaries] = [1.0, 1.0, 1.0]
    return np.clip(overlay * 255, 0, 255).astype(np.uint8)


def reset_current_analysis():
    for key in [
        "analysis_id", "current_image_rgb", "current_image_name", "current_image_path", "current_image_sha256",
        "current_labels", "current_overlay", "current_metrics", "current_method", "current_settings_snapshot"
    ]:
        st.session_state.pop(key, None)


def main():
    st.set_page_config(page_title="iPSC-Myoblast Image QC & Annotation", layout="wide")

    # Discreet language selector in the top-right area of the main page.
    top_left, top_right = st.columns([0.78, 0.22])
    with top_right:
        language_selection = st.selectbox("", ["🇧🇷 Português", "🇺🇸 English"], index=0, key="language_select", label_visibility="collapsed")
    lang = get_language_code(language_selection)
    tr = make_translator(lang)

    with top_left:
        st.title(tr("app_title"))
        st.write(tr("subtitle"))

    settings = sidebar_settings(tr, lang)
    project_or_series = st.text_input(tr("project"), value="myoblast_project")
    output_dirs = ensure_output_dirs(settings["output_dir"], project_or_series)

    # Image selection/upload.
    image_rgb_original = None
    image_name = None
    image_path_label = "uploaded_file"
    image_hash = ""

    if settings["input_mode"] == tr("upload_image"):
        uploaded = st.file_uploader(tr("choose_file"), type=["png", "jpg", "jpeg", "tif", "tiff", "bmp"])
        if uploaded is not None:
            image_rgb_original, raw = load_image_from_upload(uploaded)
            image_name = uploaded.name
            image_path_label = uploaded.name
            image_hash = sha256_bytes(raw)
    else:
        images = list_images(settings["root_dir"])
        if images:
            root_resolved = Path(settings["root_dir"]).expanduser().resolve()
            labels = []
            for p in images:
                try:
                    labels.append(str(Path(p).relative_to(root_resolved)))
                except ValueError:
                    labels.append(Path(p).name)
            selected_label = st.selectbox(tr("select_image"), labels)
            selected_path = images[labels.index(selected_label)]
            image_rgb_original = load_image_from_path(selected_path)
            image_name = Path(selected_path).name
            image_path_label = selected_path
            image_hash = sha256_file(selected_path)
        else:
            st.info("No images found in folder." if lang == "en" else "Nenhuma imagem encontrada na pasta.")

    if image_rgb_original is None:
        st.stop()

    image_rgb = resize_if_large(image_rgb_original, settings["max_side"])
    st.caption(f"{image_name} — {image_rgb.shape[1]} × {image_rgb.shape[0]} px")

    current_identity = f"{image_hash}_{settings['max_side']}_{settings['segmentation_method']}_{settings['cellpose_model_type']}_{settings['cellpose_use_gpu']}_{settings['cellpose_diameter']}_{settings['blur_kernel']}_{settings['min_object_area']}_{settings['use_adaptive_threshold']}_{settings['invert_threshold']}_{settings['elongated_threshold']}_{settings['myotube_area_threshold']}_{settings['myotube_aspect_ratio_threshold']}"
    if st.session_state.get("current_identity") != current_identity:
        # Do not run segmentation automatically; simply mark current analysis stale.
        reset_current_analysis()
        st.session_state["current_identity"] = current_identity

    run_col, status_col = st.columns([0.25, 0.75])
    with run_col:
        run_clicked = st.button(tr("run_segmentation"), type="primary")
    with status_col:
        if "current_metrics" in st.session_state:
            st.success(tr("segmentation_ready"))
        else:
            st.info(tr("no_segmentation"))

    if run_clicked:
        with st.spinner(tr("segmenting")):
            analysis_id = make_analysis_id()
            t0 = time.time()
            labels, method_used = run_segmentation(image_rgb, settings)
            overlay = create_overlay(image_rgb, labels, settings["overlay_alpha"])
            elapsed = time.time() - t0
            metrics = compute_metrics(
                labels=labels,
                image_name=image_name,
                image_path=image_path_label,
                image_sha256=image_hash,
                analysis_id=analysis_id,
                method=method_used,
                settings=settings,
                elapsed_seconds=elapsed,
            )
            st.session_state["analysis_id"] = analysis_id
            st.session_state["current_image_rgb"] = image_rgb
            st.session_state["current_image_name"] = image_name
            st.session_state["current_image_path"] = image_path_label
            st.session_state["current_image_sha256"] = image_hash
            st.session_state["current_labels"] = labels
            st.session_state["current_overlay"] = overlay
            st.session_state["current_metrics"] = metrics
            st.session_state["current_method"] = method_used
            st.session_state["current_settings_snapshot"] = settings.copy()
        st.rerun()

    records_df = load_records(output_dirs["csv"])
    tab1, tab2, tab3, tab4, tab5 = st.tabs([tr("image_overlay"), tr("metrics_legend"), tr("annotate_save"), tr("review"), tr("records")])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(tr("original"))
            st.image(image_rgb, use_container_width=True)
        with c2:
            st.subheader(tr("overlay"))
            if "current_overlay" in st.session_state:
                st.image(st.session_state["current_overlay"], use_container_width=True)
            else:
                st.info(tr("no_segmentation"))
        if "current_labels" in st.session_state:
            with st.expander(tr("binary_mask")):
                st.image(st.session_state["current_labels"] > 0, use_container_width=True)

    with tab2:
        if "current_metrics" in st.session_state:
            show_metrics(tr, st.session_state["current_metrics"], lang)
            st.warning(tr("warning_exploratory"))
        else:
            st.info(tr("no_segmentation"))

    with tab3:
        if "current_metrics" not in st.session_state:
            st.info(tr("no_segmentation"))
        else:
            annotation = annotation_form(tr, project_or_series)
            if annotation is not None:
                # Crucial: no segmentation is run here. We only use session_state outputs.
                asset_paths = save_analysis_assets(
                    analyses_dir=output_dirs["analyses"],
                    analysis_id=st.session_state["analysis_id"],
                    image_name=st.session_state["current_image_name"],
                    image_rgb=st.session_state["current_image_rgb"],
                    overlay=st.session_state["current_overlay"],
                    labels=st.session_state["current_labels"],
                )
                df = save_record(
                    csv_path=output_dirs["csv"],
                    json_path=output_dirs["json"],
                    metrics=st.session_state["current_metrics"],
                    annotation=annotation,
                    asset_paths=asset_paths,
                    settings=st.session_state["current_settings_snapshot"],
                )
                st.success(tr("saved_success"))
                st.write(f"Analysis ID: `{st.session_state['analysis_id']}`")
                st.write(f"CSV: `{output_dirs['csv']}`")
                st.write(f"Record JSON: `{Path(asset_paths['analysis_dir']) / 'record.json'}`")
                st.write(f"Original: `{asset_paths['original_image_path']}`")
                st.write(f"Overlay: `{asset_paths['overlay_path']}`")
                st.write(f"Mask: `{asset_paths['mask_path']}`")
                st.dataframe(df.tail(5), use_container_width=True)

    with tab4:
        records_df = load_records(output_dirs["csv"])
        review_previous_analyses(tr, records_df, lang)

    with tab5:
        records_df = load_records(output_dirs["csv"])
        if records_df.empty:
            st.info(tr("no_records"))
        else:
            st.dataframe(records_df, use_container_width=True)
            with open(output_dirs["csv"], "rb") as f:
                st.download_button(tr("download_csv"), data=f, file_name="records.csv", mime="text/csv")
            numeric_cols = [c for c in ["confluence_percent", "object_count", "mean_aspect_ratio", "elongated_object_percent", "myotube_candidate_count", "quality_score_1_to_5"] if c in records_df.columns]
            if numeric_cols:
                selected = st.selectbox("Metric", numeric_cols)
                st.line_chart(records_df[selected])


if __name__ == "__main__":
    main()
