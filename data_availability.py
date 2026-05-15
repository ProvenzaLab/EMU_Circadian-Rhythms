import pandas as pd
import os
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
#one file per electrode, every row is a different 10 minute thing

path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/DataInfo"
save_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/DataAval.png"

fs = 250

def calc_samples(file):
    file_path = os.path.join(path,file)
    df = pd.read_csv(file_path)
    parts = file.split("_")
    pat = parts[0]
    samples = df["NumberDataSamples"].sum()
    total_nan = df["NumberNaNs"].sum()

    return {
        "sub": pat,
        "samples": samples,
        "total_nans": total_nan
    }


files = sorted([f for f in os.listdir(path) if f.endswith(".csv")])

results = Parallel(n_jobs = 40, verbose=0)(delayed(calc_samples)(file) for file in files)

df_files = pd.DataFrame(results)

## Plotting --------------------


df_patients = df_files[df_files["samples"] > 0].sort_values("samples", ascending=False).groupby("sub", as_index=False).first()

# Convert valid samples to hours
# fs = 250 samples/sec
df_patients["seconds_available"] = df_patients["samples"] / fs
df_patients["hours_available"] = df_patients["seconds_available"] / 3600


# Total expected points = valid + nan
df_patients["total_points"] = df_patients["samples"] + df_patients["total_nans"]

# Percent missing
df_patients["percent_nan"] = (
    (df_patients["total_nans"] / df_patients["total_points"]) * 100
)

# Optional: sort so plot looks cleaner
df_patients = df_patients.sort_values("hours_available", ascending=False)
total_hours_all_electrodes = df_patients["hours_available"].sum()

print(f"\nTotal recording hours (one electrode): {total_hours_all_electrodes:,.2f}")

# Make bar plot
plt.figure(figsize=(12, 6))
bars = plt.bar(df_patients["sub"], df_patients["hours_available"])
plt.tight_layout()
plt.show()

plt.savefig(save_path,dpi=300,bbox_inches="tight",transparent = True)


# ---------------- Summary Table ----------------
summary = pd.DataFrame({
    "Metric": [
        "Number of Patients",
        "Mean Hours",
        "Median Hours",
        "Std Hours",
        "Min Hours",
        "Max Hours",
        "Mean % Missing",
        "Median % Missing"
    ],
    "Value": [
        df_patients["sub"].nunique(),
        df_patients["hours_available"].mean(),
        df_patients["hours_available"].median(),
        df_patients["hours_available"].std(),
        df_patients["hours_available"].min(),
        df_patients["hours_available"].max(),
        df_patients["percent_nan"].mean(),
        df_patients["percent_nan"].median()
    ]
})

print("\n===== DATA AVAILABILITY SUMMARY =====")
print(summary.to_string(index=False))


df_table = df_patients.copy()

df_table["hours_available"] = df_table["hours_available"].round(2)
df_table["percent_nan"] = df_table["percent_nan"].round(2)

df_table = df_table[[
    "sub",
    "hours_available",
    "percent_nan"
]].rename(columns={
    "sub": "Patient",
    "hours_available": "Hours Recorded",
    "percent_nan": "% Missing"
})

print("\n===== PER-PATIENT RECORDING =====")
print(df_table.to_string(index=False))
