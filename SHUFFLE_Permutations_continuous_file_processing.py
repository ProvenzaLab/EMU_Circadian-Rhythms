import numpy as np
import os
from datetime import datetime
import pandas as pd
from scipy.signal import welch, get_window
from scipy.optimize import curve_fit
from scipy import stats
from scipy import signal
from scipy.stats import zscore
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from fooof import FOOOF
from fooof.sim.gen import gen_aperiodic
from numpy import isnan
from datetime import timedelta
import mne

folder = "continuous_data_new" #check to see if it sampled to 250 Hz

fs = 250

f_l = [[3, 4], [4, 8], [8, 15], [15, 30], [30, 55], [65, 125]]
f_names = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]



def compute_patient_ch(file_name):

    parts = file_name.split("_")
    pat = parts[0]
    ch = parts[1]

    if os.path.exists(f"chunks_power_continuous_PERMS_new/{pat}_{ch}_powerPERMS.csv"):
        return
     
    

    full_path = os.path.join(folder,file_name)
    l_ = []
    
   
    data1 = np.load(full_path).astype(np.float64)

    for n in range(100):
        data = data1.copy()
        mask = ~np.isnan(data1)
        shuffled_vals = np.random.permutation(data1[mask])
        
        data[mask] = shuffled_vals
        
        dt_string = parts[2].replace(".npy", "")
        dt = datetime.strptime(dt_string, "%Y%m%d-%H%M%S.%f") #format example: 2024-07-21 12:30:12

        interval = (250*60*10)
        start = 0

        while start < len(data):

            data_curr = data[start:start+interval]
            start += interval

            # num_nan = np.sum(np.isnan(data_curr))
            # num_points = np.sum(~np.isnan(data_curr)) #number of points not NaN - data availability

    
            # s_.append({
            #         "sub": pat,
            #         "ch":ch,
            #         "date":dt,
            #         "NumberNaNs":num_nan,
            #         "NumberDataSamples": num_points
            #     })
            
            
            if len(data_curr) < interval: #only want 10 min chunks, you can throw the last part out
                break
                
            
            if np.sum(np.isnan(data_curr)) <= 50: #check for 3 or less NaNs and interpolate, otherwise skip
                nans = np.isnan(data_curr)
                not_nans = ~nans
                data_curr[nans] = np.interp(
                np.flatnonzero(nans),
                np.flatnonzero(not_nans),
                data_curr[not_nans]
                )
            else:
                dt = dt + timedelta(minutes=10)
                continue



            data_curr = mne.filter.notch_filter(x=data_curr,Fs=250,freqs=60) #notch filters at 60 and 120 Hz
        
            mean_data = np.mean(data_curr)
            #no z-score with FOOOF

            f,Pxx = welch(data_curr,fs=250,window ="hamming",nperseg=2500,noverlap=0,detrend="constant",scaling="density",average="mean") #nfft default set equal to nperseg

            freq_range = [3, 125] 

            fm = FOOOF(aperiodic_mode='fixed')

            try:
                fm.fit(f,Pxx,freq_range)
            except Exception as e:
                dt = dt + timedelta(minutes=10)
                continue

        
            init_ap_fit = gen_aperiodic(fm.freqs, fm._robust_ap_fit(fm.freqs, fm.power_spectrum))
            flat_spec = fm.power_spectrum - init_ap_fit
            

            for f_range,f_name in zip(f_l,f_names):
                idx = (fm.freqs>=f_range[0]) & (fm.freqs<=f_range[1])
            
                mean_power = np.mean(flat_spec[idx])
                l_.append({
                    "sub": pat,
                    "ch":ch,
                    "date":dt,
                    "feature_name": f_name,
                    "power":mean_power,
                    "permutation": n
                })
            

            l_.append({
                    "sub": pat,
                    "ch":ch,
                    "date":dt,
                    "offset": fm.aperiodic_params_[0], 
                    "exponent":fm.aperiodic_params_[1], 
                    "permutation": n
                })
            
            dt = dt + timedelta(minutes=10)


    df_power = pd.DataFrame(l_)
   
    df_power.to_csv(f"chunks_power_continuous_PERMS_new/{pat}_{ch}_powerPERMS.csv",index=False)
    

if __name__ == "__main__":
    files = sorted([f for f in os.listdir(folder) if f.endswith(".npy")])



    Parallel(n_jobs =-1 ,verbose=0)(delayed(compute_patient_ch)(path_pass) for path_pass in files)

    print("DONE.")