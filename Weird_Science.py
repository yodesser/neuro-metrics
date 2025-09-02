import os
import numpy as np
import nibabel as nib
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt


def compute_roi_table(md_data: np.ndarray, atlas_data: np.ndarray,
                      min_voxels: int = 30, trim: float = 0.025) -> pd.DataFrame:
    """
    Build a per-ROI table with robust MD statistics.
    - Drops background (label 0) and very small ROIs (n < min_voxels)
    - Winsorizes tails by `trim` on each side to reduce outlier influence
    - Reports mean/median/IQR and voxel counts
    - Scales MD to x10^-3 mm^2/s for readability
    """
    labels = np.unique(atlas_data)
    labels = labels[labels != 0]  # drop background

    rows = []
    for lab in labels:
        vals = md_data[atlas_data == lab]
        vals = vals[np.isfinite(vals)]
        if vals.size < min_voxels:
            continue

        # Robustify: winsorize tails to limit extreme outliers
        w = stats.mstats.winsorize(vals, limits=(trim, trim))
        mean_md = float(np.mean(w))
        median_md = float(np.median(w))
        q1, q3 = np.percentile(w, [25, 75])
        iqr = float(q3 - q1)

        rows.append({
            "RegionLabel": int(lab),
            "n_vox": int(vals.size),
            "MeanMD_raw": mean_md,
            "MedianMD_raw": median_md,
            "Q1_raw": float(q1),
            "Q3_raw": float(q3),
            "IQR_raw": iqr,
        })

    if not rows:
        return pd.DataFrame(columns=[
            "RegionLabel", "n_vox",
            "MeanMD", "MedianMD", "Q1", "Q3", "IQR"
        ])

    df = pd.DataFrame(rows)

    # Convert MD to x10^-3 mm^2/s (friendlier numbers on plots)
    for src, dst in [
        ("MeanMD_raw", "MeanMD"),
        ("MedianMD_raw", "MedianMD"),
        ("Q1_raw", "Q1"),
        ("Q3_raw", "Q3"),
        ("IQR_raw", "IQR"),
    ]:
        df[dst] = df[src] * 1e3

    df = df.drop(columns=[c for c in df.columns if c.endswith("_raw")])
    df = df.sort_values("MedianMD", ascending=False).reset_index(drop=True)
    return df


def plot_top_bottom(df: pd.DataFrame, topn: int = 25, out_prefix: str = "md"):
    """Save Top-N and Bottom-N horizontal bar charts and a distribution histogram."""
    if df.empty:
        print("No ROIs to plot.")
        return

    # Top-N
    sub = df.head(topn).iloc[::-1]  # reverse for barh (lowest at bottom)
    plt.figure(figsize=(9, 10))
    plt.barh(sub["RegionLabel"].astype(str), sub["MedianMD"])
    plt.xlabel("Median MD (×10⁻³ mm²/s)")
    plt.ylabel("Region")
    plt.title(f"Top {len(sub)} Regions by Median MD")
    plt.tight_layout()
    top_path = f"{out_prefix}_top{len(sub)}.png"
    plt.savefig(top_path, dpi=180)
    print(f"Saved: {top_path}")

    # Bottom-N
    sub = df.tail(topn)
    plt.figure(figsize=(9, 10))
    plt.barh(sub["RegionLabel"].astype(str), sub["MedianMD"])
    plt.xlabel("Median MD (×10⁻³ mm²/s)")
    plt.ylabel("Region")
    plt.title(f"Bottom {len(sub)} Regions by Median MD")
    plt.tight_layout()
    bottom_path = f"{out_prefix}_bottom{len(sub)}.png"
    plt.savefig(bottom_path, dpi=180)
    print(f"Saved: {bottom_path}")

    # Distribution (all ROIs)
    plt.figure(figsize=(8, 4))
    plt.hist(df["MedianMD"], bins=40)
    plt.xlabel("Median MD per ROI (×10⁻³ mm²/s)")
    plt.ylabel("Number of ROIs")
    plt.title("Distribution of ROI Median MD")
    plt.tight_layout()
    hist_path = f"{out_prefix}_hist.png"
    plt.savefig(hist_path, dpi=180)
    print(f"Saved: {hist_path}")


def main():
    # 1) Data folder next to this script (change if needed)
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    md_path = os.path.join(data_dir, "mean_diffusivity.nii")
    atlas_path = os.path.join(data_dir, "atlas_labels.nii")

    # 2) Load NIfTI images
    print("Loading NIfTI files...")
    md_img = nib.load(md_path)
    atlas_img = nib.load(atlas_path)

    md_data = md_img.get_fdata()
    atlas_data = atlas_img.get_fdata().astype(int)

    # 3) Build per-ROI table (robust)
    df = compute_roi_table(md_data, atlas_data, min_voxels=30, trim=0.025)
    if df.empty:
        print("No regions passed QC (check atlas/MD and thresholds).")
        return

    # 4) Save full table
    csv_path = "md_by_region.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved table: {csv_path}")

    # Show top rows in console
    print("\nTop 10 ROIs by Median MD (×10⁻³ mm²/s):")
    print(df[["RegionLabel", "n_vox", "MedianMD", "IQR"]].head(10).to_string(index=False))

    # 5) Plots (Top/Bottom N + histogram)
    plot_top_bottom(df, topn=25, out_prefix="md")

    # Optional: display last figure window if running interactively
    # plt.show()


if __name__ == "__main__":
    main()
