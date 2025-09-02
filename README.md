# neuro-metrics
Robust diffusion MRI pipeline for analyzing regional mean diffusivity in structural brain plasticity studies. Implements data preparation, statistical cleaning, and visualization with NumPy, SciPy, pandas, matplotlib, and NiBabel.
## Features
- **NIfTI support** — reads diffusion metrics and atlas labels via [NiBabel](https://nipy.org/nibabel/).
- **Robust statistics** — winsorization, median/IQR reporting, outlier trimming.
- **Automated QC** — filters out small/unstable ROIs.
- **Clear outputs** — CSV table of ROI metrics and publication-ready figures:
  - Top/bottom ROIs by MD
  - ROI MD distribution histogram
- **Reproducible** — lightweight Python environment (NumPy, SciPy, pandas, matplotlib).

## Quick Start

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/<your-username>/neuro-diffusion-stats.git
cd neuro-diffusion-stats

python -m venv .venv
.\.venv\Scripts\activate    # Windows
# or source .venv/bin/activate on macOS/Linux

pip install -r requirements.txt

thon src/md_roi_stats.py 
```

## Expected Outputs

  md_by_region.csv — full ROI statistics

  md_top25.png — top 25 ROIs by median MD

  md_bottom25.png — bottom 25 ROIs by median MD

  md_hist.png — distribution of ROI MD values

## Applications

Designed for coursework and exploratory projects in:

   Structural brain plasticity

   Diffusion MRI research

   Quantitative neuroimaging
