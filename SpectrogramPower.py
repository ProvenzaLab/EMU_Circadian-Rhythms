import numpy as np
import os
import pandas as pd
from scipy.stats import zscore
from joblib import Parallel, delayed
from pandas.errors import EmptyDataError
import matplotlib.pyplot as plt

PATH = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/chunks_power_continuous_new"
save_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/Heatmap.png"


def load_alpha_file(file_name):
    full_path = os.path.join(PATH, file_name)

    try:
        df = pd.read_csv(full_path)
    except EmptyDataError:
        return None 

    if df.empty:
        return None

    base = file_name.replace(".csv", "")
    parts = base.split("_")
   

    patient = parts[0]
   

    df_band = df[df["feature_name"] == "alpha"].copy()
   
    df_band["date"] = pd.to_datetime(df_band["date"])
    df_band = df_band.sort_values("date")

    full_index = pd.date_range(
    start=df_band["date"].min(),
    end=df_band["date"].max(),
    freq="10min"
    )
    
    df_band = df_band.set_index("date").reindex(full_index)
    power_series = df_band["power"].to_numpy(dtype=float)
    power_series = zscore(power_series, nan_policy="omit")
    # power_series = (
    #     pd.Series(power_series)
    #     .interpolate(limit_direction="both")
    #     .to_numpy(dtype=float)
    #     )
    


    # power_series = power_series[:864] #limit to 2 days
    # if len(power_series) < 864:
    #     return None
    

    return {
        "patient": patient,
        "df_band": power_series
    }



files = sorted([f for f in os.listdir(PATH) if f.endswith(".csv")])

loaded = Parallel(n_jobs=40, verbose=0)(
    delayed(load_alpha_file)(file_name) for file_name in files
)

loaded = [x for x in loaded if x is not None]
loaded = [x for x in loaded if x["patient"] == "YFCDatafile"]


loaded_sorted = sorted(loaded, key=lambda x: x["patient"])

all_rows = []
current_patient = None

for item in loaded_sorted:
    patient = item["patient"]
    arr = item["df_band"]

    # skip bad ones
    if arr is None or len(arr) == 0:
        continue

    
    if current_patient is not None and patient != current_patient:
        sep = np.full((1, arr.shape[0]), np.nan)
        all_rows.append(sep)

    all_rows.append(arr[None, :])  # make it 2D row
    current_patient = patient

matrix = np.vstack(all_rows)

cmap = plt.cm.viridis.copy()
cmap.set_bad(color="black") #set NaNs to black color

plt.figure(figsize=(12, 6))

plt.imshow(
    matrix,
    aspect="auto",
    origin="lower",
    interpolation="nearest",
    cmap=cmap,
    vmin=0,
    vmax=0.8
)

plt.xlabel("Time (hours)", fontsize=14)
plt.ylabel("Electrode",fontsize=14)
plt.title("Z-scored Alpha Power Heatmap",fontsize=20)
plt.colorbar(label="Z-score")

ticks = np.arange(0, matrix.shape[1], 72)
labels = np.arange(0, len(ticks) * 12, 12)

plt.xticks(ticks=ticks, labels=labels)

plt.tight_layout()
plt.show()
plt.savefig(save_path, dpi=300, bbox_inches="tight", transparent = True)