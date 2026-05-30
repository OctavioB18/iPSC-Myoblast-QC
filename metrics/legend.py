import pandas as pd


def get_metrics_legend(lang: str) -> pd.DataFrame:
    if lang == "pt":
        rows = [
            ("image_name", "Nome do arquivo analisado.", "Identifica qual foto foi avaliada."),
            ("image_path", "Caminho completo ou origem da imagem.", "Permite rastrear ou reprocessar a imagem."),
            ("timestamp", "Data e horário da análise.", "Útil para histórico e auditoria."),
            ("segmentation_method", "Método de segmentação usado.", "OpenCV é rápido; Cellpose tende a ser melhor, mas mais lento."),
            ("confluence_percent", "Percentual da imagem ocupado por objetos segmentados.", "Maior valor sugere maior confluência ou densidade celular."),
            ("object_count", "Número total de objetos detectados.", "Pode representar células, agrupamentos ou fragmentos."),
            ("mean_object_area_px", "Área média dos objetos.", "Aumenta com células maiores, agregados ou miotubos."),
            ("mean_aspect_ratio", "Razão média comprimento/largura.", "Valores altos indicam morfologia alongada/fusiforme."),
            ("mean_circularity", "Circularidade média.", "Próximo de 1 indica objetos arredondados."),
            ("elongated_object_percent", "Percentual de objetos alongados.", "Útil para acompanhar alinhamento e morfologia miogênica."),
            ("myotube_candidate_count", "Número de possíveis miotubos.", "Estimativa exploratória de objetos grandes e alongados."),
            ("quality_score_1_to_5", "Nota subjetiva de qualidade.", "Útil para triagem rápida de imagens/condições."),
            ("exclude_from_analysis", "Indica exclusão da análise consolidada.", "Mantém o registro, mas permite filtrar depois."),
        ]
        return pd.DataFrame(rows, columns=["Coluna", "Significado", "Interpretação prática"])

    rows = [
        ("image_name", "Analyzed image file name.", "Identifies which image was evaluated."),
        ("image_path", "Full path or source of the image.", "Allows tracing or reprocessing the image."),
        ("timestamp", "Analysis date and time.", "Useful for history and auditability."),
        ("segmentation_method", "Segmentation method used.", "OpenCV is fast; Cellpose may be better but slower."),
        ("confluence_percent", "Percentage of the image occupied by segmented objects.", "Higher values suggest higher confluence or cell density."),
        ("object_count", "Total number of detected objects.", "May represent cells, clusters, or fragments."),
        ("mean_object_area_px", "Mean object area.", "Increases with larger cells, aggregates, or myotubes."),
        ("mean_aspect_ratio", "Mean length/width ratio.", "High values indicate elongated/fusiform morphology."),
        ("mean_circularity", "Mean circularity.", "Close to 1 indicates rounded objects."),
        ("elongated_object_percent", "Percentage of elongated objects.", "Useful to monitor alignment and myogenic morphology."),
        ("myotube_candidate_count", "Number of possible myotubes.", "Exploratory estimate of large elongated objects."),
        ("quality_score_1_to_5", "Subjective quality score.", "Useful for rapid screening across images/conditions."),
        ("exclude_from_analysis", "Whether to exclude from consolidated analysis.", "Keeps the record but allows filtering later."),
    ]
    return pd.DataFrame(rows, columns=["Column", "Meaning", "Practical interpretation"])
