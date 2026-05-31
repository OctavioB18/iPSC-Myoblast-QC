# iPSC-Myoblast Image QC & Annotation

A Streamlit-based research tool for exploratory image quality control and annotation during iPSC-to-myoblast/myotube differentiation workflows.

## Key features

- Select images using the system file picker or from a project folder.
- Run segmentation with either:
  - fast OpenCV-based segmentation, or
  - optional Cellpose segmentation.
- Keep segmentation results in session memory so saving annotations does **not** rerun segmentation.
- Generate a unique `analysis_id` for every segmentation run.
- Save a traceable analysis package containing:
  - original image used for analysis,
  - segmentation mask,
  - overlay image,
  - metrics JSON,
  - annotation JSON,
  - combined record JSON.
- Maintain project-level `records.csv` and `records.json` files.
- Review previous analyses with original image, overlay, mask, metrics, and annotations.
- Bilingual UI: Portuguese and English.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional Cellpose support:

```bash
pip install -r requirements-cellpose.txt
```

## Running the app

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Recommended workflow

1. Select an image using the file picker or from the `images/` folder.
2. Adjust segmentation parameters in the sidebar.
3. Click **Run segmentation**.
4. Inspect original image, overlay, and binary mask.
5. Fill in manual annotations.
6. Click **Save Annotation**.
7. Review past analyses in the review tab.

## Output structure

For each project, outputs are saved as:

```text
outputs/
└── Project_Name/
    ├── analyses/
    │   └── 20260531_145501_ab12cd34/
    │       ├── original.png
    │       ├── overlay.png
    │       ├── mask.tif
    │       ├── metrics.json
    │       ├── annotation.json
    │       └── record.json
    └── tables/
        ├── records.csv
        └── records.json
```

The `analysis_id` links every image, mask, overlay, metric set, and manual annotation.

## Notes on Cellpose and Apple Silicon

On some Apple Silicon systems, Cellpose may be much faster when GPU is enabled. If CPU execution appears extremely slow, try enabling the GPU checkbox in the sidebar.

## Scientific note

The metrics provided by this app are exploratory. Myogenic maturation and fusion should be validated with appropriate markers and, when possible, nuclear/immunofluorescence-based analysis.
