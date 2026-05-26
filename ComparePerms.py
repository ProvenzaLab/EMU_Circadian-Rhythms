import pandas as pd
import numpy as np
import os


PERMpath = '/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_PERMS_new'
path = '/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new'
files=[]
files2=[]
for root,dirs,fs in os.walk(path):
    for file in fs:
        files.append(os.path.join(root,file))

df_real = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


# Load permutation values
for root,dirs,fs in os.walk(PERMpath):
    for file in fs:
        files2.append(os.path.join(root,file))

df_perm = pd.concat([pd.read_csv(f) for f in files2],ignore_index=True)

# Merge on patient, Label, frequency_band
df_merged = df_real.merge(
    df_perm[["patient", "Label", "frequency_band", "permutation", "circadian_power_24hr", "exponent_power_24hr", "offset_power_24hr"]],
    on=["patient", "Label", "frequency_band"],
    suffixes=("_real", "_perm")
)
def compute_pvalue(group, metric):
    real_val = group[f"{metric}_real"].iloc[0]
    p_val = (group[f"{metric}_perm"] >= real_val).sum() / 100
    return p_val

summary = []

# Power — per patient/electrode/band
df_pvals_power = (
    df_merged
    .groupby(["patient", "Label", "frequency_band"])
    .apply(lambda g: compute_pvalue(g, "circadian_power_24hr"))
    .reset_index()
    .rename(columns={0: "p_value"})
)


n_total = len(df_pvals_power)
summary.append({
    "metric": "circadian_power_24hr",
    "p<0.05 (%)": (df_pvals_power["p_value"] < 0.05).sum() / n_total * 100,
    "p<0.01 (%)": (df_pvals_power["p_value"] < 0.01).sum() / n_total * 100,
})

# Exponent and offset — per patient/electrode only
for metric in ["exponent_power_24hr", "offset_power_24hr"]:
    df_pvals = (
        df_merged
        .groupby(["patient", "Label"])
        .apply(lambda g: compute_pvalue(g, metric))
        .reset_index()
        .rename(columns={0: "p_value"})
    )
    n_total = len(df_pvals)
    summary.append({
        "metric": metric,
        "p<0.05 (%)": (df_pvals["p_value"] < 0.05).sum() / n_total * 100,
        "p<0.01 (%)": (df_pvals["p_value"] < 0.01).sum() / n_total * 100,
    })

df_summary = pd.DataFrame(summary)
print(df_summary)
