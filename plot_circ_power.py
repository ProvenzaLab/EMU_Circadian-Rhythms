from matplotlib import pyplot as plt
import pandas as pd
import os
import numpy as np
import seaborn as sns

bands = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]
df_power_24 = pd.read_csv("circ_power/circadian_power_24hr_summary.csv")

max_shuffled = df_power_24.query("shuffled")["power_24hr"].mean()
count_chs = df_power_24.groupby(["patient", "channel"]).count().reset_index()
print(df_power_24.query("shuffled == False and power_24hr > @max_shuffled").shape[0] / (count_chs.shape[0] * len(bands)))

for band in bands:
    print(band)
    max_shuffled = df_power_24.query("shuffled and band == @band")["power_24hr"].mean()
    count_chs = df_power_24.query("band == @band").groupby(["patient", "channel"]).count().reset_index()
    print(df_power_24.query("shuffled == False and power_24hr > @max_shuffled and band == @band").shape[0] / (count_chs.shape[0]))


plt.figure(figsize=(4, 3))
sns.histplot(data=df_power_24, x="power_24hr", hue="shuffled", common_norm=False, bins=200)
# make log x and y axis
#plt.xscale("log")
plt.yscale("log")
plt.savefig("figures/circadian_power_24hr_histogram_shuffled.pdf")

plt.figure()
sns.histplot(data=df_power_24.query("shuffled == False"), x="power_24hr", hue="band",
             multiple="stack", common_norm=False, bins=200)
# make log x and y axis
#plt.xscale("log")
#plt.yscale("log")
plt.savefig("figures/circadian_power_24hr_histogram_bands.png", dpi=300)


plt.figure(figsize=(10, 25))
for idx_band, band in enumerate(bands):
    plt.subplot(len(bands), 1, idx_band + 1)
    df_band = df_power_24[df_power_24["band"] == band]
    sns.boxplot(x="patient", y="power_24hr", data=df_band)
    #sns.swarmplot(x="patient", y="power_24hr", data=df_band, color=".25")
    plt.xticks(rotation=90)
    plt.title(f"{band}")
plt.tight_layout()
plt.savefig("figures/circadian_power_24hr_violinplots.png", dpi=300)

df_sub = df_power_24[df_power_24["patient"] == "YFADatafile"]
df_sub_delta = df_sub[df_sub["band"] == "delta"]

plt.figure(figsize=(10, 5))
sns.barplot(x="channel", y="power_24hr", data=df_sub_delta)
plt.xticks(rotation=90)
plt.title(f"YFADatafile - delta band")
plt.tight_layout()
plt.savefig("figures/circadian_power_24hr_YFA_delta_channel_boxplot.png", dpi=300)