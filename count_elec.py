import numpy as np
import os
import pandas as pd


path1 = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"
df_all = []


for root,dirs,files in os.walk(path1):
    for file in files:
        df = pd.read_csv(os.path.join(root,file))
        df_all.append(df)


df_all = pd.concat(df_all,ignore_index = True)
df_all = df_all[df_all["frequency_band"] == "alpha"]
df_all = df_all.drop_duplicates(subset=["patient", "Label"])

total_electrodes = df_all.shape[0]

# ---- electrodes per patient ----
electrodes_per_patient = df_all.groupby("patient").size()

# ---- average electrodes per patient ----
avg_electrodes = electrodes_per_patient.mean()
std_electrodes = electrodes_per_patient.std()

# ---- print ----
print(f"Total electrodes: {total_electrodes}")
print(f"Average electrodes per patient: {avg_electrodes:.2f}")
print(f"STD electrodes per patient: {std_electrodes:.2f}")
