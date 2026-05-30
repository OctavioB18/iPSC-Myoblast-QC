from __future__ import annotations

from typing import List

from models import AutoMetrics


def biological_interpretation(metrics: AutoMetrics, lang: str) -> List[str]:
    pt = lang == "pt"

    if metrics.object_count == 0:
        return [
            "Nenhum objeto foi detectado. Ajuste threshold, área mínima ou inverta o threshold."
            if pt else
            "No objects were detected. Adjust threshold, minimum area, or invert threshold."
        ]

    interpretation = []

    if pt:
        if metrics.confluence_percent < 20:
            interpretation.append("Baixa confluência: cultura esparsa ou segmentação conservadora.")
        elif metrics.confluence_percent < 50:
            interpretation.append("Confluência intermediária: compatível com expansão ou início de diferenciação.")
        elif metrics.confluence_percent < 80:
            interpretation.append("Confluência alta: pode favorecer alinhamento e início de fusão celular.")
        else:
            interpretation.append("Confluência muito alta: possível cultura densa, fusão avançada ou supersegmentação.")

        if metrics.mean_aspect_ratio >= 3:
            interpretation.append("Razão de aspecto média elevada: há tendência de morfologia alongada/fusiforme.")
        else:
            interpretation.append("Razão de aspecto média baixa: objetos mais arredondados ou pouco alongados.")

        if metrics.elongated_object_percent >= 30:
            interpretation.append("Percentual alto de objetos alongados: pode sugerir alinhamento miogênico.")
        elif metrics.elongated_object_percent >= 10:
            interpretation.append("Percentual moderado de objetos alongados: possível início de diferenciação/alinhamento.")
        else:
            interpretation.append("Poucos objetos alongados detectados.")

        if metrics.myotube_candidate_percent >= 20:
            interpretation.append("Quantidade relevante de candidatos a miotubos detectada; confirme com marcadores e/ou análise nuclear.")
        elif metrics.myotube_candidate_count > 0:
            interpretation.append("Alguns candidatos a miotubos foram detectados.")
        else:
            interpretation.append("Nenhum candidato claro a miotubo foi detectado com os limiares atuais.")

        if metrics.mean_circularity > 0.75:
            interpretation.append("Circularidade média alta: muitos objetos parecem arredondados, possivelmente estágio menos diferenciado ou estresse.")
    else:
        if metrics.confluence_percent < 20:
            interpretation.append("Low confluence: sparse culture or conservative segmentation.")
        elif metrics.confluence_percent < 50:
            interpretation.append("Intermediate confluence: consistent with expansion or early differentiation.")
        elif metrics.confluence_percent < 80:
            interpretation.append("High confluence: may favor alignment and early cell fusion.")
        else:
            interpretation.append("Very high confluence: dense culture, advanced fusion, or over-segmentation.")

        if metrics.mean_aspect_ratio >= 3:
            interpretation.append("High mean aspect ratio: elongated/fusiform morphology is present.")
        else:
            interpretation.append("Low mean aspect ratio: objects are more rounded or weakly elongated.")

        if metrics.elongated_object_percent >= 30:
            interpretation.append("High percentage of elongated objects: may suggest myogenic alignment.")
        elif metrics.elongated_object_percent >= 10:
            interpretation.append("Moderate percentage of elongated objects: possible early differentiation/alignment.")
        else:
            interpretation.append("Few elongated objects detected.")

        if metrics.myotube_candidate_percent >= 20:
            interpretation.append("Relevant number of myotube candidates detected; confirm with markers and/or nuclear analysis.")
        elif metrics.myotube_candidate_count > 0:
            interpretation.append("Some myotube candidates were detected.")
        else:
            interpretation.append("No clear myotube candidates were detected with the current thresholds.")

        if metrics.mean_circularity > 0.75:
            interpretation.append("High mean circularity: many objects appear rounded, possibly less differentiated or stressed.")

    return interpretation
