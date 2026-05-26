import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import signal
from tqdm import tqdm
from joblib import Parallel, delayed
import random

FS = 250  # Hz
SNIPPET_DURATION = 10  # seconds
N_SNIPPETS = 10
SAMPLES_PER_SNIPPET = FS * SNIPPET_DURATION

PATH_IN = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/continuous_data_new"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data_quality_check"
os.makedirs(PATH_OUT, exist_ok=True)


def process_file(fpath: str):
    fname = os.path.basename(fpath)
    # strip .npy extension and timestamp suffix → use full stem as pdf name
    stem = fname.replace(".npy", "")
    out_pdf = os.path.join(PATH_OUT, stem + "_quality.pdf")

    if os.path.exists(out_pdf):
        return  # skip already done

    try:
        data = np.load(fpath)
    except Exception as e:
        print(f"Error loading {fname}: {e}")
        return

    if data.ndim != 1:
        print(f"Skipping {fname}: unexpected shape {data.shape}")
        return

    n_total = len(data)
    if n_total < SAMPLES_PER_SNIPPET:
        print(f"Skipping {fname}: too short ({n_total} samples)")
        return

    # possible snippet start indices (non-overlapping, aligned to snippet size)
    max_start = n_total - SAMPLES_PER_SNIPPET
    # pick N_SNIPPETS random start positions
    random.seed(42)
    starts = sorted(random.sample(range(0, max_start, SAMPLES_PER_SNIPPET), 
                                  min(N_SNIPPETS, max_start // SAMPLES_PER_SNIPPET)))
    # if not enough non-overlapping windows, fall back to uniform random
    if len(starts) < N_SNIPPETS:
        starts = sorted(random.sample(range(0, max_start), min(N_SNIPPETS, max_start)))

    n_rows = len(starts)
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 3 * n_rows))
    if n_rows == 1:
        axes = axes[np.newaxis, :]

    fig.suptitle(stem, fontsize=9, y=1.001)

    t10 = np.arange(SAMPLES_PER_SNIPPET) / FS
    t1 = np.arange(FS) / FS  # 1-second zoom

    for row, start in enumerate(starts):
        snippet = data[start: start + SAMPLES_PER_SNIPPET]

        # --- 10 s plot ---
        ax = axes[row, 0]
        ax.plot(t10, snippet, linewidth=0.4, color="steelblue")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.set_xlabel("Time [s]", fontsize=7)
        ax.set_ylabel("Amplitude", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_title(f"start={start/FS:.1f}s", fontsize=7)

        # --- 1 s zoom ---
        ax = axes[row, 1]
        ax.plot(t1, snippet[:FS], linewidth=0.4, color="steelblue")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.set_xlabel("Time [s]", fontsize=7)
        ax.set_ylabel("Amplitude", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_title("1 s zoom", fontsize=7)

        # --- PSD ---
        ax = axes[row, 2]
        snip_clean = np.nan_to_num(snippet, nan=0.0)
        f, Pxx = signal.welch(snip_clean, fs=FS, nperseg=FS)
        ax.plot(f, np.log(Pxx + 1e-30), linewidth=0.5, color="darkorange")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.set_xlabel("Frequency [Hz]", fontsize=7)
        ax.set_ylabel("log PSD", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_title("PSD (Welch)", fontsize=7)

    plt.tight_layout()
    try:
        with PdfPages(out_pdf) as pdf:
            pdf.savefig(fig, bbox_inches="tight")
    except Exception as e:
        print(f"Error saving PDF for {fname}: {e}")
    finally:
        plt.close(fig)


if __name__ == "__main__":
    npy_files = sorted([
        os.path.join(PATH_IN, f)
        for f in os.listdir(PATH_IN)
        if f.endswith(".npy")
    ])
    print(f"Found {len(npy_files)} .npy files")

    already_done = {
        f.replace("_quality.pdf", "") for f in os.listdir(PATH_OUT) if f.endswith("_quality.pdf")
    }
    npy_files = [fp for fp in npy_files if os.path.basename(fp).replace(".npy", "") not in already_done]
    print(f"{len(npy_files)} files remaining (skipping already processed)")

    Parallel(n_jobs=-1)(
        delayed(process_file)(fp) for fp in tqdm(npy_files, desc="Quality check")
    )
    print("Done. PDFs saved to:", PATH_OUT)
