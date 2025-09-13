# Doc2LaTeX AI Pipeline — Overleaf‑ready Starter Kit

## Quick Start
1. Install TeX Live/MiKTeX, pandoc, tesseract (optional).
2. Create a Python venv and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Place your input DOCX/PDF/TXT in `input/`.
4. Run conversion:
   ```bash
   python src/convert.py --in input/sample.docx --template pro_report --meta config/docmeta.yaml --brand config/brand.yaml --out output/overleaf_project --build
   ```
5. Zip for Overleaf:
   ```bash
   python src/export/pack_overleaf.py --src output/overleaf_project --zip output/overleaf_project.zip
   ```
