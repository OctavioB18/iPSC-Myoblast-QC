
from __future__ import annotations

from typing import Dict, List
import pandas as pd

# This dictionary is deliberately keyed by actual dataframe column names.
# The legend table is generated dynamically from df.columns, so it can never
# show descriptions for columns that are not actually displayed.
COLUMN_INFO: Dict[str, Dict[str, Dict[str, str]]] = {
    "image_name": {
        "pt": {"meaning": "Nome do arquivo analisado.", "practical": "Identifica qual foto foi avaliada.", "range": "Texto"},
        "en": {"meaning": "Analyzed file name.", "practical": "Identifies which image was evaluated.", "range": "Text"},
    },
    "image_path": {
        "pt": {"meaning": "Caminho completo ou origem da imagem.", "practical": "Permite rastrear ou reprocessar a imagem.", "range": "Texto"},
        "en": {"meaning": "Full path or source of the image.", "practical": "Allows tracking or reprocessing the image.", "range": "Text"},
    },
    "timestamp": {
        "pt": {"meaning": "Data e horário da análise.", "practical": "Útil para histórico e auditoria.", "range": "ISO datetime"},
        "en": {"meaning": "Analysis date and time.", "practical": "Useful for history and audit trails.", "range": "ISO datetime"},
    },
    "segmentation_method": {
        "pt": {"meaning": "Método usado para segmentar a imagem.", "practical": "Ajuda a comparar resultados entre OpenCV e Cellpose.", "range": "Texto"},
        "en": {"meaning": "Method used to segment the image.", "practical": "Helps compare OpenCV and Cellpose results.", "range": "Text"},
    },
    "image_width_px": {
        "pt": {"meaning": "Largura da imagem analisada.", "practical": "Importante para comparar imagens de resoluções diferentes.", "range": "Pixels"},
        "en": {"meaning": "Width of the analyzed image.", "practical": "Important when comparing images with different resolutions.", "range": "Pixels"},
    },
    "image_height_px": {
        "pt": {"meaning": "Altura da imagem analisada.", "practical": "Importante para comparar imagens de resoluções diferentes.", "range": "Pixels"},
        "en": {"meaning": "Height of the analyzed image.", "practical": "Important when comparing images with different resolutions.", "range": "Pixels"},
    },
    "confluence_percent": {
        "pt": {"meaning": "Percentual da área da imagem marcado como célula/objeto pela segmentação.", "practical": "Maior valor sugere maior confluência, densidade celular ou segmentação mais inclusiva.", "range": "0–100 %"},
        "en": {"meaning": "Percentage of image area labeled as cell/object by segmentation.", "practical": "Higher values suggest greater confluence, cell density, or more inclusive segmentation.", "range": "0–100 %"},
    },
    "object_count": {
        "pt": {"meaning": "Número de objetos conectados detectados após segmentação.", "practical": "Pode representar células individuais, grupos celulares, miotubos ou fragmentos.", "range": "Contagem"},
        "en": {"meaning": "Number of connected objects detected after segmentation.", "practical": "May represent individual cells, cell clusters, myotubes, or fragments.", "range": "Count"},
    },
    "mean_object_area_px": {
        "pt": {"meaning": "Área média dos objetos segmentados.", "practical": "Aumenta quando objetos são maiores, quando há agregados ou estruturas semelhantes a miotubos.", "range": "px²"},
        "en": {"meaning": "Mean area of segmented objects.", "practical": "Increases with larger objects, aggregates, or myotube-like structures.", "range": "px²"},
    },
    "median_object_area_px": {
        "pt": {"meaning": "Mediana da área dos objetos segmentados.", "practical": "Mais robusta que a média quando há poucos objetos muito grandes.", "range": "px²"},
        "en": {"meaning": "Median area of segmented objects.", "practical": "More robust than the mean when a few very large objects exist.", "range": "px²"},
    },
    "mean_major_axis_px": {
        "pt": {"meaning": "Média do comprimento do maior eixo dos objetos.", "practical": "Tende a aumentar quando as células/estruturas ficam mais alongadas.", "range": "Pixels"},
        "en": {"meaning": "Mean length of the objects' major axis.", "practical": "Usually increases as cells/structures become more elongated.", "range": "Pixels"},
    },
    "mean_minor_axis_px": {
        "pt": {"meaning": "Média do comprimento do menor eixo dos objetos.", "practical": "Relaciona-se à largura/espessura dos objetos segmentados.", "range": "Pixels"},
        "en": {"meaning": "Mean length of the objects' minor axis.", "practical": "Related to object width/thickness.", "range": "Pixels"},
    },
    "mean_aspect_ratio": {
        "pt": {"meaning": "Média da razão entre maior eixo e menor eixo.", "practical": "Valores maiores indicam morfologia mais alongada/fusiforme.", "range": "≥ 1"},
        "en": {"meaning": "Mean ratio between major axis and minor axis.", "practical": "Higher values indicate more elongated/spindle-like morphology.", "range": "≥ 1"},
    },
    "median_aspect_ratio": {
        "pt": {"meaning": "Mediana da razão entre maior eixo e menor eixo.", "practical": "Resume alongamento típico reduzindo influência de objetos extremos.", "range": "≥ 1"},
        "en": {"meaning": "Median ratio between major axis and minor axis.", "practical": "Summarizes typical elongation while reducing influence from outliers.", "range": "≥ 1"},
    },
    "mean_circularity": {
        "pt": {"meaning": "Circularidade média calculada como 4π·área/perímetro².", "practical": "Próximo de 1 indica objetos arredondados; menor indica objetos alongados/irregulares.", "range": "0–1 aprox."},
        "en": {"meaning": "Mean circularity calculated as 4π·area/perimeter².", "practical": "Near 1 indicates round objects; lower values indicate elongated/irregular objects.", "range": "Approx. 0–1"},
    },
    "elongated_object_count": {
        "pt": {"meaning": "Número de objetos com razão de aspecto acima do limiar configurado.", "practical": "Ajuda a estimar células/estruturas alongadas.", "range": "Contagem"},
        "en": {"meaning": "Number of objects with aspect ratio above the configured threshold.", "practical": "Helps estimate elongated cells/structures.", "range": "Count"},
    },
    "elongated_object_percent": {
        "pt": {"meaning": "Percentual de objetos classificados como alongados.", "practical": "Útil para acompanhar alinhamento e aquisição de morfologia miogênica.", "range": "0–100 %"},
        "en": {"meaning": "Percentage of objects classified as elongated.", "practical": "Useful for tracking alignment and acquisition of myogenic morphology.", "range": "0–100 %"},
    },
    "myotube_candidate_count": {
        "pt": {"meaning": "Número de objetos grandes e alongados que passam nos limiares de candidato a miotubo.", "practical": "Estimativa exploratória; não substitui validação por marcadores/núcleos.", "range": "Contagem"},
        "en": {"meaning": "Number of large elongated objects passing myotube-candidate thresholds.", "practical": "Exploratory estimate; does not replace marker/nuclear validation.", "range": "Count"},
    },
    "myotube_candidate_percent": {
        "pt": {"meaning": "Percentual de objetos classificados como possíveis miotubos.", "practical": "Pode sugerir fusão/maturação, mas depende da qualidade da segmentação.", "range": "0–100 %"},
        "en": {"meaning": "Percentage of objects classified as possible myotubes.", "practical": "May suggest fusion/maturation, but depends on segmentation quality.", "range": "0–100 %"},
    },
    "project_or_series": {
        "pt": {"meaning": "Nome do projeto, série ou experimento.", "practical": "Organiza registros por contexto experimental.", "range": "Texto"},
        "en": {"meaning": "Project, series, or experiment name.", "practical": "Organizes records by experimental context.", "range": "Text"},
    },
    "researcher": {
        "pt": {"meaning": "Nome/identificação do pesquisador.", "practical": "Rastreia quem fez a anotação.", "range": "Texto"},
        "en": {"meaning": "Researcher name/identifier.", "practical": "Tracks who made the annotation.", "range": "Text"},
    },
    "cell_line": {
        "pt": {"meaning": "Linhagem iPSC usada.", "practical": "Permite comparar linhagens.", "range": "Texto"},
        "en": {"meaning": "iPSC cell line used.", "practical": "Allows comparison between cell lines.", "range": "Text"},
    },
    "differentiation_day": {
        "pt": {"meaning": "Dia do protocolo de diferenciação.", "practical": "Essencial para acompanhar progressão temporal.", "range": "Dias"},
        "en": {"meaning": "Day of the differentiation protocol.", "practical": "Essential for tracking temporal progression.", "range": "Days"},
    },
    "protocol_name": {
        "pt": {"meaning": "Nome do protocolo usado.", "practical": "Permite comparar protocolos.", "range": "Texto"},
        "en": {"meaning": "Name of the protocol used.", "practical": "Allows comparison between protocols.", "range": "Text"},
    },
    "medium": {
        "pt": {"meaning": "Meio de cultivo utilizado.", "practical": "Ajuda a relacionar condição de cultivo e morfologia.", "range": "Texto"},
        "en": {"meaning": "Culture medium used.", "practical": "Helps relate culture conditions and morphology.", "range": "Text"},
    },
    "supplements_or_factors": {
        "pt": {"meaning": "Suplementos/fatores adicionados.", "practical": "Registra moduladores do protocolo.", "range": "Texto"},
        "en": {"meaning": "Supplements/factors added.", "practical": "Records protocol modulators.", "range": "Text"},
    },
    "coating_matrix": {
        "pt": {"meaning": "Matriz/revestimento usado.", "practical": "Pode afetar adesão, alinhamento e fusão.", "range": "Texto"},
        "en": {"meaning": "Coating matrix used.", "practical": "May affect adhesion, alignment, and fusion.", "range": "Text"},
    },
    "passage_number": {
        "pt": {"meaning": "Número de passagem celular.", "practical": "Passagens podem afetar comportamento celular.", "range": "Texto/número"},
        "en": {"meaning": "Cell passage number.", "practical": "Passage may affect cell behavior.", "range": "Text/number"},
    },
    "seeding_density": {
        "pt": {"meaning": "Densidade de plaqueamento.", "practical": "Influencia confluência, alinhamento e fusão.", "range": "Texto/número"},
        "en": {"meaning": "Seeding density.", "practical": "Influences confluence, alignment, and fusion.", "range": "Text/number"},
    },
    "last_medium_change": {
        "pt": {"meaning": "Última troca de meio.", "practical": "Ajuda a interpretar estresse ou morte celular.", "range": "Texto/data"},
        "en": {"meaning": "Last medium change.", "practical": "Helps interpret stress or cell death.", "range": "Text/date"},
    },
    "expected_stage": {
        "pt": {"meaning": "Estágio esperado pelo protocolo.", "practical": "Permite comparar esperado vs observado.", "range": "Categoria"},
        "en": {"meaning": "Expected protocol stage.", "practical": "Allows expected vs observed comparison.", "range": "Category"},
    },
    "observed_stage": {
        "pt": {"meaning": "Estágio observado pelo pesquisador.", "practical": "Registra interpretação humana.", "range": "Categoria"},
        "en": {"meaning": "Stage observed by the researcher.", "practical": "Records human interpretation.", "range": "Category"},
    },
    "markers_tested": {
        "pt": {"meaning": "Marcadores avaliados.", "practical": "Ex.: PAX7, MYOD1, MYOG, MYHC.", "range": "Texto"},
        "en": {"meaning": "Markers tested.", "practical": "E.g., PAX7, MYOD1, MYOG, MYHC.", "range": "Text"},
    },
    "marker_result_summary": {
        "pt": {"meaning": "Resumo dos resultados de marcadores.", "practical": "Conecta morfologia com identidade/maturação celular.", "range": "Texto"},
        "en": {"meaning": "Marker result summary.", "practical": "Connects morphology with cell identity/maturation.", "range": "Text"},
    },
    "contamination_signs": {
        "pt": {"meaning": "Avaliação visual de contaminação.", "practical": "Ajuda a sinalizar imagens problemáticas.", "range": "Categoria"},
        "en": {"meaning": "Visual assessment of contamination.", "practical": "Helps flag problematic images.", "range": "Category"},
    },
    "stress_or_death_signs": {
        "pt": {"meaning": "Avaliação de estresse ou morte celular.", "practical": "Ajuda a interpretar baixa qualidade ou perda celular.", "range": "Categoria"},
        "en": {"meaning": "Assessment of stress or cell death.", "practical": "Helps interpret low quality or cell loss.", "range": "Category"},
    },
    "quality_score_1_to_5": {
        "pt": {"meaning": "Nota subjetiva de qualidade da imagem/cultura.", "practical": "Útil para triagem rápida.", "range": "1–5"},
        "en": {"meaning": "Subjective image/culture quality score.", "practical": "Useful for quick screening.", "range": "1–5"},
    },
    "exclude_from_analysis": {
        "pt": {"meaning": "Indica se a imagem deve ser excluída de análises consolidadas.", "practical": "Mantém o registro, mas permite filtrar depois.", "range": "True/False"},
        "en": {"meaning": "Indicates whether the image should be excluded from consolidated analyses.", "practical": "Keeps the record but allows later filtering.", "range": "True/False"},
    },
    "free_notes": {
        "pt": {"meaning": "Observações livres.", "practical": "Registra informações não capturadas pelas métricas.", "range": "Texto"},
        "en": {"meaning": "Free notes.", "practical": "Records information not captured by metrics.", "range": "Text"},
    },
}

def build_legend(columns: List[str], lang: str = "pt") -> pd.DataFrame:
    rows = []
    labels = {
        "pt": ("Coluna", "Significado", "Interpretação prática", "Faixa/Unidade"),
        "en": ("Column", "Meaning", "Practical interpretation", "Range/Unit"),
    }
    col_label, meaning_label, practical_label, range_label = labels.get(lang, labels["en"])

    for col in columns:
        if str(col).startswith("Unnamed:"):
            continue
        info = COLUMN_INFO.get(col, {}).get(lang)
        if info is None:
            info = {
                "meaning": "Sem descrição disponível." if lang == "pt" else "No description available.",
                "practical": "Coluna gerada pelo programa ou adicionada externamente." if lang == "pt" else "Column generated by the program or externally added.",
                "range": "-",
            }
        rows.append({
            col_label: col,
            meaning_label: info["meaning"],
            practical_label: info["practical"],
            range_label: info["range"],
        })
    return pd.DataFrame(rows)
