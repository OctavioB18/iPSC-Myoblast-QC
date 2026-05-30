
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from metrics.interpretation import biological_interpretation
from metrics.legend import build_legend
from translations import tr

def show_metrics(metrics, elapsed_seconds: float, lang: str):
    st.subheader(tr(lang, "automatic_metrics"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr(lang, "confluence"), f"{metrics.confluence_percent:.1f}%")
    c2.metric(tr(lang, "objects"), metrics.object_count)
    c3.metric(tr(lang, "elongated"), f"{metrics.elongated_object_percent:.1f}%")
    c4.metric(tr(lang, "myotubes"), metrics.myotube_candidate_count)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(tr(lang, "mean_ar"), f"{metrics.mean_aspect_ratio:.2f}")
    c6.metric(tr(lang, "circularity"), f"{metrics.mean_circularity:.2f}")
    c7.metric(tr(lang, "mean_area"), f"{metrics.mean_object_area_px:.0f} px²")
    c8.metric(tr(lang, "time"), f"{elapsed_seconds:.2f} s")

    st.subheader(tr(lang, "bio_interpretation"))
    for item in biological_interpretation(metrics, lang):
        st.info(item)

    metrics_df = pd.DataFrame([asdict(metrics)])

    with st.expander(tr(lang, "complete_table"), expanded=True):
        st.dataframe(metrics_df, use_container_width=True)

    with st.expander(tr(lang, "legend"), expanded=True):
        st.dataframe(build_legend(metrics_df.columns.tolist(), lang), use_container_width=True)

def show_saved_records(csv_path: Path, lang: str):
    if not csv_path.exists():
        st.info(tr(lang, "no_records"))
        return

    st.subheader(tr(lang, "saved_records"))
    df = pd.read_csv(csv_path)
    # Drop legacy accidental index columns if present
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed:")]
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
        selected = st.selectbox(tr(lang, "metric_plot"), available)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(len(df)), df[selected], marker="o")
        ax.set_xlabel("Registro" if lang == "pt" else "Record")
        ax.set_ylabel(selected)
        ax.set_title(selected)
        st.pyplot(fig)

    with st.expander(tr(lang, "legend")):
        st.dataframe(build_legend(df.columns.tolist(), lang), use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(tr(lang, "download_csv"), data=csv_bytes, file_name=csv_path.name, mime="text/csv")
