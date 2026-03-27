import pandas as pd
import os
import numpy as np
import pickle
import seaborn as sns
from matplotlib import pyplot as plt


bands = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

l_ = []

for PATH_DATA in ["circ_power", "circ_power_shuffled"]:
    if "shuffled" in PATH_DATA:
        SHUFFLED = True
    else: 
        SHUFFLED = False

    files = [f for f in os.listdir(PATH_DATA) if f.endswith(".pkl")]
    if SHUFFLED:
        patient_names = [f.split("_")[-2] for f in files]
    else:
        patient_names = [f.split("_")[-1][:-4] for f in files]

    for f_idx, file in enumerate(files):
        patient = patient_names[f_idx]

        with open(os.path.join(PATH_DATA, file), "rb") as f:
            d_ = pickle.load(f)

        chs = list(d_.keys())

        for ch in chs:
            d_ch = d_[ch]
            for band_idx, band in enumerate(bands):
                psd_c = d_ch["band_circ_power"][band_idx]
                tp = d_ch["period_hr_r"]
                # get tp index closest to 24 hours
                idx_24 = np.where(tp.round(2) == 24)[0]
                power_24 = psd_c[idx_24][0]
                tp_24 = tp[idx_24]
                l_.append({"patient": patient, "channel": ch, "band": band, "power_24hr": power_24, "shuffled": SHUFFLED})

df_power_24 = pd.DataFrame(l_)
df_power_24.to_csv("circ_power/circadian_power_24hr_summary.csv", index=False)

plt.figure()
sns.histplot(data=df_power_24.query("shuffled == False and band == 'delta'"), x="power_24hr", hue="patient", common_norm=False, multiple="stack", bins=50)
plt.tight_layout()
plt.savefig("figures/circadian_power_24hr_histogram(new).png", dpi=300)

plt.figure()
sns.histplot(data=df_power_24.query("band == 'delta'"), x="power_24hr", hue="shuffled", common_norm=False, bins=200)
# make log x and y axis
#plt.xscale("log")
plt.yscale("log")
plt.savefig("figures/circadian_power_24hr_histogram_shuffled(new).png", dpi=300)

plt.figure(figsize=(10, 15))
for idx_band, band in enumerate(bands):
    plt.subplot(len(bands), 1, idx_band + 1)
    df_band = df_power_24[df_power_24["band"] == band]
    sns.boxplot(x="patient", y="power_24hr", data=df_band)
    #sns.swarmplot(x="patient", y="power_24hr", data=df_band, color=".25")
    plt.xticks(rotation=90)
    plt.title(f"{band}")
plt.tight_layout()
plt.savefig("figures/circadian_power_24hr_violinplots(new).png", dpi=300)