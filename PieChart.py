import numpy as np
import os
import pandas as pd
from scipy.stats import zscore
from joblib import Parallel, delayed
from pandas.errors import EmptyDataError
import matplotlib.pyplot as plt
import matplotlib.cm as cm


PATH = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"
save_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/PieChartAlpha.png"
all_alpha = []
for root, dirs, files in os.walk(PATH):
   
    for file in files:
        if not file.endswith(".csv"):
            continue

        full_path = os.path.join(root, file)

        try:
            df = pd.read_csv(full_path)
        except EmptyDataError:
            continue

        if df.empty:
            continue


        df_alpha = df[df["frequency_band"] == "alpha"].copy()
        

        if df_alpha.empty:
            continue

        
        df_alpha = df_alpha[~df_alpha["Label"].str.contains("empty", case=False, na=False)]
        df_alpha["region_clean"] = df_alpha["Label"].str.replace(r"[-\d]+$", "", regex=True)
       

        df_alpha = df_alpha[["region_clean", "circadian_power_24hr"]].dropna()


        all_alpha.append(df_alpha)


df_all_alpha = pd.concat(all_alpha, ignore_index=True)

# average alpha power within each region across all appearances
df_region_mean = (
    df_all_alpha
    .groupby("region_clean", as_index=False)["circadian_power_24hr"]
    .mean()
    .rename(columns={"circadian_power_24hr": "mean_alpha_power"})
)

# top 10 regions
top10_regions = df_region_mean.sort_values(
    by="mean_alpha_power",
    ascending=False
).head(10)

total_power = top10_regions["mean_alpha_power"].sum()

fractions = top10_regions["mean_alpha_power"] / total_power

plt.figure(figsize=(7,7))
colors = cm.Reds(np.linspace(0.4, 1, len(top10_regions)))

plt.pie(
    fractions,
    labels=top10_regions["region_clean"],
    autopct="%1.1f%%",
    colors=colors
)

plt.title("Top 10 Alpha Power Regions",fontsize=20)
plt.tight_layout()
plt.show()
plt.savefig(save_path, dpi=300, bbox_inches="tight", transparent = True)
