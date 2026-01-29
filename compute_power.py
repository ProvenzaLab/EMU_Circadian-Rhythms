import numpy as np
import os
from datetime import datetime
import pandas as pd
from scipy.signal import welch, get_window
from scipy.optimize import curve_fit
from scipy import stats
from scipy.stats import zscore
import matplotlib.pyplot as plt
from tqdm import tqdm
from joblib import Parallel, delayed

folder = "chunks_out_fixed"
pt = "YFA"

fs = 250

l_ = []

f_l = [[0, 4], [4, 8], [8, 15], [15, 30], [30, 55], [65, 125]]
f_names = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

def compute_patient_ch(patient_folder, ch):
    new_fol = os.path.join(folder, patient_folder)   
    l_ = []
    for file in tqdm(os.listdir(os.path.join(new_fol, ch))):
        full_path = os.path.join(new_fol, ch, file)
        data = np.load(full_path).astype(np.float64)
        parts = file.split("_") # YFADatafile_empty-128_20240423-060301
        sub = file.split("_")[0]
        ch = file.split("_")[1]
        dt_string = parts[2].replace(".npy", "")
        dt = datetime.strptime(dt_string, "%Y%m%d-%H%M%S")
        data = zscore(data)
        f, Pxx = welch(data,fs=250,window ="hamming",nperseg=250,noverlap=125,nfft=256,detrend="constant",scaling="density",average="mean")
        
        for f_range, f_name in zip(f_l, f_names):
            idx = (f >= f_range[0]) & (f < f_range[1])
            mean_power = np.mean(Pxx[idx])
            l_.append({
                "sub" : sub,
                "ch" : ch,
                "date" : dt,
                "band": f_name,
                "power": mean_power
            })
    df_power = pd.DataFrame(l_)
    df_power.to_csv(f"chunks_power/{patient_folder}_{ch}_power.csv", index=False)
    print(f"Saved power for {patient_folder} {ch}")
    # df_plt = df_power.query("band == 'delta'")
    # # sort by date
    # df_plt = df_plt.sort_values(by="date")
    # df_ts = df_plt["date"]
    # plt.figure(figsize=(12, 4))
    # plt.plot(df_ts, df_plt["power"])
    # plt.savefig(f"test_power_{sub}_{ch}_delta.png")


patients = sorted(os.listdir(folder))[:7]

for i, patient_folder in enumerate(patients): 
    new_fol = os.path.join(folder, patient_folder)   
    chs = os.listdir(new_fol)
    #compute_patient_ch(patient_folder, chs[0])  # compute for the first channel to avoid overloading the system
    Parallel(n_jobs=20, verbose=0)(delayed(compute_patient_ch)(patient_folder, ch) for ch in chs)

# run using nohup python compute_power.py > compute_power.log 2>&1 &