from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from metrics.interpretation import biological_interpretation
from metrics.legend import get_metrics_legend
from models import AutoMetrics


def show_metrics(metrics: AutoMetrics, elapsed_seconds: float, lang: str, tr):
    st.subheader(tr("auto_metrics"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("confluence"), f"{metrics.confluence_percent:.1f}%")
    c2.metric(tr("objects"), metrics.object_count)
    c3.metric(tr("elongated"), f"{metrics.elongated_object_percent:.1f}%")
    c4.metric(tr("myotube_candidates"), metrics.myotube_candidate_count)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(tr("aspect_ratio"), f"{metrics.mean_aspect_ratio:.2f}")
    c6.metric(tr("circularity"), f"{metrics.mean_circularity:.2f}")
    c7.metric(tr("mean_area"), f"{metrics.mean_object_area_px:.0f} px")
    c8.metric(tr("time"), f"{elapsed_seconds:.2f} s")

    st.subheader(tr("bio_interpretation"))
    for item in biological_interpretation(metrics, lang):
        st.info(item)

    with st.expander(tr("full_metrics")):
        st.dataframe(pd.DataFrame([asdict(metrics)]), use_container_width=True)

    with st.expander(tr("legend")):
        st.dataframe(get_metrics_legend(lang), use_container_width=True)


def show_saved_records(csv_path: Path, tr):
    if not csv_path.exists():
        st.info(tr("no_records"))
        return

    st.subheader(tr("saved_records"))
    df = pd.read_csv(csv_path)
    st.dataframe(df.tail(30), use_container_width=True)

    numeric_cols = [
        "confluence_percent",
        "object_count",
        "mean_aspect_ratio",
        "elongated_object_percent",
        "myotube_candidate_count",
        "quality_score_1_to_5",
    ]
    available = [c for c in numeric_cols if c in df.columns]

    if available:
        selected = st.selectbox(tr("visualize_metric"), available)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(len(df)), df[selected], marker="o")
        ax.set_xlabel("Record")
        ax.set_ylabel(selected)
        ax.set_title(selected)
        st.pyplot(fig)

    with open(csv_path, "rb") as f:
        st.download_button(tr("download_csv"), data=f, file_name=csv_path.name, mime="text/csv")
