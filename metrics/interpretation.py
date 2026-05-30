
from __future__ import annotations

from typing import List
from metrics.morphology import AutoMetrics

def biological_interpretation(metrics: AutoMetrics, lang: str = "pt") -> List[str]:
    if metrics.object_count == 0:
        return [
            "Nenhum objeto foi detectado. Ajuste threshold, área mínima ou inverta o threshold."
            if lang == "pt"
            else "No objects were detected. Adjust threshold, minimum area, or invert threshold."
        ]

    if lang == "pt":
        items = []
        if metrics.confluence_percent < 20:
            items.append("Baixa confluência: cultura esparsa ou segmentação conservadora.")
        elif metrics.confluence_percent < 50:
            items.append("Confluência intermediária: compatível com expansão ou início de diferenciação.")
        elif metrics.confluence_percent < 80:
            items.append("Confluência alta: pode favorecer alinhamento e início de fusão celular.")
        else:
            items.append("Confluência muito alta: possível cultura densa, fusão avançada ou supersegmentação.")

        if metrics.mean_aspect_ratio >= 3:
            items.append("Razão de aspecto média elevada: tendência de morfologia alongada/fusiforme.")
        else:
            items.append("Razão de aspecto média baixa: objetos mais arredondados ou pouco alongados.")

        if metrics.elongated_object_percent >= 30:
            items.append("Percentual alto de objetos alongados: pode sugerir alinhamento miogênico.")
        elif metrics.elongated_object_percent >= 10:
            items.append("Percentual moderado de objetos alongados: possível início de diferenciação/alinhamento.")
        else:
            items.append("Poucos objetos alongados detectados.")

        if metrics.myotube_candidate_percent >= 20:
            items.append("Quantidade relevante de candidatos a miotubos detectada; confirme com marcadores e/ou análise nuclear.")
        elif metrics.myotube_candidate_count > 0:
            items.append("Alguns candidatos a miotubos foram detectados.")
        else:
            items.append("Nenhum candidato claro a miotubo foi detectado com os limiares atuais.")
        return items

    items = []
    if metrics.confluence_percent < 20:
        items.append("Low confluence: sparse culture or conservative segmentation.")
    elif metrics.confluence_percent < 50:
        items.append("Intermediate confluence: compatible with expansion or early differentiation.")
    elif metrics.confluence_percent < 80:
        items.append("High confluence: may favor alignment and early cell fusion.")
    else:
        items.append("Very high confluence: possible dense culture, advanced fusion, or over-segmentation.")

    if metrics.mean_aspect_ratio >= 3:
        items.append("High mean aspect ratio: elongated/spindle-like morphology trend.")
    else:
        items.append("Low mean aspect ratio: more rounded or weakly elongated objects.")

    if metrics.elongated_object_percent >= 30:
        items.append("High percentage of elongated objects: may suggest myogenic alignment.")
    elif metrics.elongated_object_percent >= 10:
        items.append("Moderate percentage of elongated objects: possible early differentiation/alignment.")
    else:
        items.append("Few elongated objects detected.")

    if metrics.myotube_candidate_percent >= 20:
        items.append("Relevant number of myotube candidates detected; confirm with markers and/or nuclear analysis.")
    elif metrics.myotube_candidate_count > 0:
        items.append("Some myotube candidates were detected.")
    else:
        items.append("No clear myotube candidates detected with current thresholds.")
    return items
