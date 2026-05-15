import numpy as np
import os
from datetime import datetime
import pandas as pd
from scipy.stats import zscore
from joblib import Parallel, delayed
from scipy.signal import welch, get_window
from pandas.errors import EmptyDataError

# Input folder: one CSV per electrode
PATH = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/chunks_power_continuous_new"

# Output folder: one CSV per patient
OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/circ_power_continuous_new"

save_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"

F_NAMES = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]


def compute_electrode_bands(file_name):
    full_path = os.path.join(PATH, file_name)

    
   
    try:
        df = pd.read_csv(full_path)
    except EmptyDataError:
        return

    base = file_name.replace(".csv", "")
    parts = base.split("_")

    patient = parts[0]
    electrode = parts[1]

    results = []

    for band in F_NAMES:


        df_band = df[df["feature_name"] == band].copy()
        df_exponent = df[df["exponent"].notna()].copy()

        df_exponent["date"] = pd.to_datetime(df_exponent["date"])
        df_band["date"] = pd.to_datetime(df_band["date"])

        df_band = df_band.sort_values("date")
        df_exponent = df_exponent.sort_values("date")



        #------- Construct full timeline
        full_index = pd.date_range(
        start=df_band["date"].min(),
        end=df_band["date"].max(),
        freq="10min"
        )
        full_index_exponent = pd.date_range(
        start=df_exponent["date"].min(),
        end=df_band["date"].max(),
        freq="10min"
        )

       
        oup1 = os.path.join("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/csvCHECK",f"debug_{patient}_{electrode}_{band}_with_BEFORE.csv")
       # df_band.to_csv(oup1)
        df_exponent = df_exponent.set_index("date").reindex(full_index_exponent)
        df_band = df_band.set_index("date").reindex(full_index)
        oup2 = os.path.join("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/csvCHECK",f"debug_{patient}_{electrode}_{band}_with_nans.csv")
       # df_band.to_csv(oup2)

        power_series = df_band["power"].to_numpy(dtype=float)

        
        exponent_series = df_exponent["exponent"].to_numpy(dtype=float)
        offset_series = df_exponent["offset"].to_numpy(dtype=float)
        #-------


        # if all values are identical, zscore returns nan
        if np.all(np.isnan(power_series)) or len(power_series) == 0 or np.nanstd(power_series) == 0:
         
            power_24hr = np.nan
            matched_period_hr = np.nan
        else:
            
            power_z = zscore(power_series, nan_policy="omit")
            power_z = (
            pd.Series(power_z)
            .interpolate(limit_direction="both")
            .to_numpy(dtype=float)
            )

            fs_ = 1/600
            nperseg_ = len(power_z)
            f, Pxx = welch(power_z,fs=fs_,window ="hamming",nperseg = nperseg_,noverlap=0,detrend="constant",scaling="density",average="mean")
        
            target_f = 1 / (24 * 3600) #24 hour frequency
            idx_24 = np.argmin(np.abs(f - target_f))
            power_24hr = Pxx[idx_24]
            matched_f = f[idx_24]
            if matched_f == 0:
                matched_period_hr = np.nan
                power_24hr = np.nan
            else:
                matched_period_hr = (1 / matched_f) / 3600 #period in hours
                if not (20 <= matched_period_hr <= 28):
                    power_24hr = np.nan
                    matched_period_hr = np.nan
        
               

        if np.all(np.isnan(exponent_series)) or len(exponent_series) == 0 or np.nanstd(exponent_series) == 0:
    
            exp_24hr = np.nan
           
        else:
            
            exp_z = zscore(exponent_series, nan_policy="omit")
            exp_z = (
            pd.Series(exp_z)
            .interpolate(limit_direction="both")
            .to_numpy(dtype=float)
            )

            fs_ = 1/600
            nperseg_ = len(exp_z)
            f, Pxx = welch(exp_z,fs=fs_,window ="hamming",nperseg = nperseg_,noverlap=0,detrend="constant",scaling="density",average="mean")
        
            target_f = 1 / (24 * 3600) #24 hour frequency
            idx_24 = np.argmin(np.abs(f - target_f))
            exp_24hr = Pxx[idx_24]
            matched_f = f[idx_24]
            if matched_f == 0:
                exp_24hr = np.nan
            else:
                matched_period_hr_exp = (1 / matched_f) / 3600 #period in hours
                if not (20 <= matched_period_hr_exp <= 28):
                    exp_24hr = np.nan

        if np.all(np.isnan(offset_series)) or len(offset_series) == 0 or np.nanstd(offset_series) == 0:
    
            off_24hr = np.nan
         
        else:
            
            off_z = zscore(offset_series, nan_policy="omit")
            off_z = (
            pd.Series(off_z)
            .interpolate(limit_direction="both")
            .to_numpy(dtype=float)
            )

            fs_ = 1/600
            nperseg_ = len(off_z)
            f, Pxx = welch(off_z,fs=fs_,window ="hamming",nperseg = nperseg_,noverlap=0,detrend="constant",scaling="density",average="mean")
        
            target_f = 1 / (24 * 3600) #24 hour frequency
            idx_24 = np.argmin(np.abs(f - target_f))
            off_24hr = Pxx[idx_24]
            matched_f = f[idx_24]
            if matched_f == 0:
                off_24hr = np.nan
            else:
                matched_period_hr_off = (1 / matched_f) / 3600 #period in hours
                if not (20 <= matched_period_hr_off <= 28):
                    off_24hr = np.nan
      



        results.append({
            "patient": patient,
            "Label": electrode,
            "frequency_band": band,
            "circadian_power_24hr": power_24hr,
            "24-hour_period": matched_period_hr,
            "exponent_power_24hr": exp_24hr,
            "offset_power_24hr": off_24hr
        })

    out_df = pd.DataFrame(results)
    patient = patient.replace("Datafile","")
    out_path0 = os.path.join(OUT,patient)
    os.makedirs(out_path0, exist_ok=True)
    out_path = os.path.join(out_path0, f"{patient}_{electrode}_circadian.csv")
    out_df.to_csv(out_path, index=False)


files = sorted([f for f in os.listdir(PATH) if f.endswith(".csv")])

Parallel(n_jobs=40, verbose=0)(
    delayed(compute_electrode_bands)(file_name) for file_name in files[:1]
)


for folder in os.listdir(OUT):
    new_path = os.path.join(OUT,folder)
    dfs = []

    for file in os.listdir(new_path):
        file_p = os.path.join(new_path,file)
        df = pd.read_csv(file_p)
        dfs.append(df)

    if dfs:
        df_combined = pd.concat(dfs, axis=0, ignore_index=True)
        save_path0 = os.path.join(save_path,folder)
        os.makedirs(save_path0, exist_ok=True)
        out_path = os.path.join(save_path0, f"{folder}_ALL_ELECTRODES.csv")
        df_combined.to_csv(out_path, index=False)


print("DONE.")