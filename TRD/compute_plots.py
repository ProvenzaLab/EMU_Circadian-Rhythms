import os
import pandas as pd
import matplotlib.pyplot as plt
from pandas.errors import EmptyDataError

os.chdir("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms")

power_dir = "chunks_power"
plot_dir = "chunks_power_plots_subplots"
os.makedirs(plot_dir, exist_ok=True)

files = sorted([f for f in os.listdir(power_dir) if f.endswith(".csv")])
bands = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

for file in files:
    path = os.path.join(power_dir, file)

    if os.path.getsize(path) == 0:
        print(f"Skipping empty file: {path}")
        continue

    try:
        df = pd.read_csv(path)
    except EmptyDataError:
        print(f"Skipping file with no columns: {path}")
        continue
    except Exception as e:
        print(f"Skipping unreadable file {path}: {e}")
        continue

    if df.empty:
        print(f"Skipping file with no rows: {path}")
        continue

    if not {"date", "band", "power"}.issubset(df.columns):
        print(f"Skipping malformed file: {path}")
        continue

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        print(f"Skipping file with invalid dates: {path}")
        continue

    fig, axes = plt.subplots(6, 1, figsize=(14, 16), sharex=True)

    for ax, band in zip(axes, bands):
        df_band = df[df["band"] == band].sort_values("date")

        if df_band.empty:
            ax.set_title(band)
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            ax.set_ylabel("Power")
            continue

        ax.plot(df_band["date"], df_band["power"])
        ax.set_title(band)
        ax.set_ylabel("Power")

    axes[-1].set_xlabel("Time")
    fig.suptitle(file.replace(".csv", ""), y=0.995)
    plt.tight_layout()

    out_path = os.path.join(plot_dir, file.replace(".csv", ".png"))
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
