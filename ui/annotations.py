
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import streamlit as st
from translations import tr

@dataclass
class ManualAnnotation:
    project_or_series: str
    image_name: str
    researcher: str
    cell_line: str
    differentiation_day: int
    protocol_name: str
    medium: str
    supplements_or_factors: str
    coating_matrix: str
    passage_number: str
    seeding_density: str
    last_medium_change: str
    expected_stage: str
    observed_stage: str
    markers_tested: str
    marker_result_summary: str
    contamination_signs: str
    stress_or_death_signs: str
    quality_score_1_to_5: int
    exclude_from_analysis: bool
    free_notes: str

def annotation_form(lang: str, project_or_series: str, image_name: str) -> Optional[ManualAnnotation]:
    st.subheader(tr(lang, "manual_annotations"))

    expected_options_pt = ["iPSC", "Mesoderma", "Progenitor miogênico", "Mioblasto", "Miotubo inicial", "Miotubo maduro", "Outro/indefinido"]
    expected_options_en = ["iPSC", "Mesoderm", "Myogenic progenitor", "Myoblast", "Early myotube", "Mature myotube", "Other/undefined"]
    observed_options_pt = ["Compatível com esperado", "iPSC-like", "Progenitor", "Mioblasto", "Miotubo", "Muita morte celular", "Contaminação/suspeita", "Indefinido"]
    observed_options_en = ["Compatible with expected", "iPSC-like", "Progenitor", "Myoblast", "Myotube", "High cell death", "Contamination/suspected", "Undefined"]

    with st.form("annotation_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            researcher = st.text_input(tr(lang, "researcher"), value="")
            cell_line = st.text_input(tr(lang, "cell_line"), value="")
            differentiation_day = st.number_input(tr(lang, "diff_day"), min_value=0, max_value=365, value=0, step=1)
        with c2:
            protocol_name = st.text_input(tr(lang, "protocol"), value="")
            medium = st.text_input(tr(lang, "medium"), value="")
            supplements_or_factors = st.text_area(tr(lang, "supplements"), value="", height=80)
        with c3:
            coating_matrix = st.text_input(tr(lang, "coating"), value="Matrigel / Laminin / other" if lang == "en" else "Matrigel / Laminina / outro")
            passage_number = st.text_input(tr(lang, "passage"), value="")
            seeding_density = st.text_input(tr(lang, "seeding"), value="")

        c4, c5 = st.columns(2)
        with c4:
            last_medium_change = st.text_input(tr(lang, "last_medium_change"), value="")
            expected_stage = st.selectbox(tr(lang, "expected_stage"), expected_options_pt if lang == "pt" else expected_options_en)
            observed_stage = st.selectbox(tr(lang, "observed_stage"), observed_options_pt if lang == "pt" else observed_options_en)
        with c5:
            markers_tested = st.text_input(tr(lang, "markers"), value="PAX7, MYOD1, MYOG, MYHC")
            marker_result_summary = st.text_area(tr(lang, "marker_summary"), value="", height=80)
            quality_score = st.slider(tr(lang, "quality"), 1, 5, 3)

        c6, c7 = st.columns(2)
        with c6:
            contamination_signs = st.selectbox(tr(lang, "contamination"), ["Não observado", "Suspeito", "Confirmado", "Não avaliado"] if lang == "pt" else ["Not observed", "Suspected", "Confirmed", "Not assessed"])
        with c7:
            stress_or_death_signs = st.selectbox(tr(lang, "stress"), ["Baixo", "Moderado", "Alto", "Não avaliado"] if lang == "pt" else ["Low", "Moderate", "High", "Not assessed"])

        free_notes = st.text_area(tr(lang, "notes"), value="", height=120)
        exclude_from_analysis = st.checkbox(tr(lang, "exclude"), value=False)
        submitted = st.form_submit_button(tr(lang, "save_annotation"))

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
