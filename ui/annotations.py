from __future__ import annotations

from typing import Optional

import streamlit as st

from models import ManualAnnotation


def annotation_form(project_or_series: str, image_name: str, tr) -> Optional[ManualAnnotation]:
    st.subheader(tr("manual_annotations"))

    with st.form("annotation_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)

        with c1:
            researcher = st.text_input(tr("researcher"), value="")
            cell_line = st.text_input(tr("cell_line"), value="")
            differentiation_day = st.number_input(tr("differentiation_day"), min_value=0, max_value=365, value=0, step=1)

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
            expected_stage = st.selectbox(
                tr("expected_stage"),
                ["iPSC", "Mesoderm", "Myogenic progenitor", "Myoblast", "Early myotube", "Mature myotube", "Other/undefined"],
            )
            observed_stage = st.selectbox(
                tr("observed_stage"),
                ["Compatible with expected", "iPSC-like", "Progenitor", "Myoblast", "Myotube", "High cell death", "Contamination/suspected", "Undefined"],
            )

        with c5:
            markers_tested = st.text_input(tr("markers"), value="PAX7, MYOD1, MYOG, MYHC")
            marker_result_summary = st.text_area(tr("marker_summary"), value="", height=80)
            quality_score = st.slider(tr("quality"), 1, 5, 3)

        c6, c7 = st.columns(2)
        with c6:
            contamination_signs = st.selectbox(tr("contamination"), ["Not observed", "Suspected", "Confirmed", "Not evaluated"])
        with c7:
            stress_or_death_signs = st.selectbox(tr("stress"), ["Low", "Moderate", "High", "Not evaluated"])

        free_notes = st.text_area(tr("notes"), value="", height=120)
        exclude_from_analysis = st.checkbox(tr("exclude"), value=False)

        submitted = st.form_submit_button(tr("save_record"))

    if not submitted:
        return None

    return ManualAnnotation(
        project_or_series=project_or_series,
        image_name=image_name,
        researcher=researcher,
        cell_line=cell_line,
        differentiation_day=int(differentiation_day),
        protocol_name=protocol_name,
        medium=medium,
        supplements_or_factors=supplements_or_factors,
        coating_matrix=coating_matrix,
        passage_number=passage_number,
        seeding_density=seeding_density,
        last_medium_change=last_medium_change,
        expected_stage=expected_stage,
        observed_stage=observed_stage,
        markers_tested=markers_tested,
        marker_result_summary=marker_result_summary,
        contamination_signs=contamination_signs,
        stress_or_death_signs=stress_or_death_signs,
        quality_score_1_to_5=int(quality_score),
        exclude_from_analysis=bool(exclude_from_analysis),
        free_notes=free_notes,
    )
