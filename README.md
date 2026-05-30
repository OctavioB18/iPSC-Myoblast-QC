# iPSC-Myoblast Image QC & Annotation

A lightweight Streamlit application for exploratory image annotation, segmentation, and morphological quality control during iPSC-to-myoblast/myotube differentiation workflows.

The tool was designed for research projects involving cultured meat, skeletal muscle differentiation, and microscopy-based quality control.

## Features

- Select images from anywhere on your computer using the Streamlit file picker.
- Optional folder-based image browsing for batch-like workflows.
- Bilingual interface: Portuguese and English.
- Fast OpenCV segmentation.
- Optional Cellpose segmentation.
- Segmentation overlay directly on the microscopy image.
- Automatic morphological metrics:
  - confluence percentage
  - detected object count
  - mean and median object area
  - major/minor axis length
  - aspect ratio
  - circularity
  - elongated object percentage
  - myotube candidate count
- Manual annotation form for experimental metadata.
- CSV and JSON export.
- Overlay and mask export.
- Saved-record dashboard with plots.

## Project structure

```text
myoblast-tracker-v2/
├── app.py
├── config.py
├── models.py
├── translations.py
├── requirements.txt
├── requirements-cellpose.txt
├── README.md
├── images/
├── outputs/
├── metrics/
│   ├── interpretation.py
│   ├── legend.py
│   └── morphology.py
├── segmentation/
│   ├── cellpose_segmentation.py
│   ├── opencv_segmentation.py
│   └── pipeline.py
├── ui/
│   ├── annotations.py
│   ├── dashboard.py
│   ├── sidebar.py
│   └── visualization.py
└── utils/
    ├── image_ops.py
    └── io.py
```

## Installation

Python 3.10 or 3.11 is recommended.

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

pip install --upgrade pip
pip install -r requirements.txt
```


## Running the app

From the project root:

```bash
streamlit run app.py
```


## Selecting images

The application supports two image input modes:

1. **Choose image from computer**  
   Opens the system file picker through Streamlit. This is the recommended mode when images are stored in different directories.

2. **Use image folder**  
   Reads images from the folder specified in the sidebar. By default, this is the `images/` folder.

Supported image formats:

- PNG
- JPG/JPEG
- TIF/TIFF
- BMP

## Output files

Results are saved under:

```text
outputs/<project_name>/
```

The app creates:

```text
outputs/<project_name>/tables/annotations_and_metrics.csv
outputs/<project_name>/tables/annotations_and_metrics.json
outputs/<project_name>/overlays/
outputs/<project_name>/masks/
```

## Notes on segmentation

### OpenCV

OpenCV segmentation is fast and usually works well for quick exploratory analysis. It is the recommended default mode.

### Cellpose

Cellpose may provide better cellular segmentation, but it is slower and can be more difficult to install depending on the computer and Python environment.

On Apple Silicon Macs, GPU acceleration may not work out of the box. If Cellpose is slow or unstable, use the OpenCV option.

## Scientific limitations

The software provides exploratory image-derived metrics. It does not replace biological validation.

Myotube candidates and maturation-related metrics should be interpreted together with:

- MYOD1
- MYOG
- MYHC/MYH markers
- nuclear staining
- immunofluorescence
- protocol timing
- experimental metadata

## License

MIT License.
