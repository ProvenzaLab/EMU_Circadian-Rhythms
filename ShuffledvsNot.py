import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

#concatenate one long csv for shuffled and not shuffled

path1 = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"
path2 = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_SHUFFLED_new"








df_not_shuffled = []
df_shuffled = []

for root,dirs,files in os.walk(path1):
    for file in files:
        df = pd.read_csv(os.path.join(root,file))
        df_not_shuffled.append(df)

for root,dirs,files in os.walk(path2):
    for file in files:
        df = pd.read_csv(os.path.join(root,file))
        df_shuffled.append(df)

df_not_shuffled = pd.concat(df_not_shuffled,ignore_index=True)
df_shuffled = pd.concat(df_shuffled,ignore_index = True)




df_not_shuffled = df_not_shuffled.sort_values(
    ["patient", "Label", "frequency_band"]
).reset_index(drop=True)

df_shuffled = df_shuffled.sort_values(
    ["patient", "Label", "frequency_band"]
).reset_index(drop=True)

# band = "high_gamma"  # change this each time

# df_not_shuffled = df_not_shuffled[df_not_shuffled["frequency_band"] == band]
# df_shuffled  = df_shuffled[df_shuffled["frequency_band"] == band]


assert len(df_not_shuffled) == len(df_shuffled), "Row count mismatch"

assert list(df_not_shuffled.columns) == list(df_shuffled.columns), "Column mismatch"

assert (df_not_shuffled["patient"].values == df_shuffled["patient"].values).all(), "pat mismatch"

assert (df_not_shuffled["Label"].values == df_shuffled["Label"].values).all(), "Label mismatch"

assert (df_not_shuffled["frequency_band"].values == df_shuffled["frequency_band"].values).all(), "freq mismatch"


greater = (df_not_shuffled["circadian_power_24hr"] >
           df_shuffled["circadian_power_24hr"]).sum()

percent = (greater/(len(df_not_shuffled))) * 100


print(percent)


plt.figure(figsize=(8,5))
plt.hist(df_not_shuffled["circadian_power_24hr"], bins=10000,alpha = 0.5,label="Not Shuffled")
plt.hist(df_shuffled["circadian_power_24hr"], bins=10000,alpha = 0.5,label="Shuffled")
plt.xscale("log")

plt.xlabel("Circadian Power (a.u.)",fontsize=14)
plt.ylabel("Count",fontsize=14)
plt.title("Circadian Modulation",fontsize=20)
plt.legend()

plt.savefig("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/histogram.png",transparent = True)
plt.show()

