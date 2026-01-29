import pandas as pd
import os
import numpy as np
from scipy import signal, stats
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
import pickle
from joblib import Parallel, delayed

PATH_DATA = "chunks_power"
band_vals = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

files_ = [f for f in os.listdir(PATH_DATA) if f.endswith("_power.csv")]
subjects = sorted(list(set([f.split("_")[0] for f in files_])))


def compute_file_sub_ch(file, SHUFFLE=False):
#file = files_sub[0]
    sub = file.split("_")[0]
    ch = file.split("_")[1]
    df = pd.read_csv(os.path.join(PATH_DATA, file))
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    # set index 
    df = df.set_index("date")
    # resample to 10 minute intervals, mean power
    df_g = df.groupby("band")["power"].resample("10T").mean().interpolate(method='linear').reset_index()
    if SHUFFLE:
        df_g = df_g.groupby("band").apply(lambda x: x.assign(power=np.random.permutation(x["power"].values))).reset_index(drop=True)

    band_circ_power = []
    df_g_l = []
    period_hr_r = None
    for band in band_vals:
        df_band = df_g[df_g["band"] == band]
        # ok, difference is now aways 10 minutes
        power_ = df_band["power"].values
        # np.where(np.isnan(power_))
        # I want to run a welch's method on this time series to get the circadian power
        power_zs = stats.zscore(power_)
        fs = 1 / (10 * 60) 

        # data is in 10 min intervals,
        # i want to clip at the lower day
        # check first that length is > 144
        if power_zs.shape[0] < 144:
            continue
        power_zs_d = power_zs[:(power_zs.shape[0] // 144) * 144]
        f, Pxx = signal.welch(power_zs_d, fs=fs, nperseg=power_zs_d.shape[0])

        period_hr = 1 / f[1:] / 3600
        period_hr_r = period_hr[::-1]
        Pxx_r = Pxx[1:][::-1]
        band_circ_power.append(Pxx_r)
        df_g_l.append(df_band)
    return band_circ_power, df_g_l, period_hr_r, sub, ch

#for subject in subjects:

def run_sub(subject, SHUFFLE=False):
    files_sub = [f for f in files_ if subject in f]
    if SHUFFLE:
        pdf_path = f"figures/circadian_power_{subject}_shuffled.pdf"
    else:
        pdf_path = f"figures/circadian_power_{subject}.pdf"
    pdf_ = PdfPages(pdf_path)
    d_sub = {}
    for file in tqdm(files_sub):
        band_circ_power, df_g_l, period_hr_r, sub, ch = compute_file_sub_ch(file, SHUFFLE=SHUFFLE)
        # if band_circ_power[0] has only nan, skip
        if len(band_circ_power) == 0:
            continue

        if np.all(np.isnan(band_circ_power[0])):
            continue
        d_sub[ch] = {
            "band_circ_power": band_circ_power,
            "df_g_l": df_g_l,
            "period_hr_r": period_hr_r
        }


        plt.figure(figsize=(12, 5))
        plt.subplot(121)
        plt.plot(df_g_l[0]["date"], df_g_l[0]["power"])
        # remove upper and right spines
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.ylabel(f"Power {band_vals[0]} z-scored")
        plt.xticks(rotation=45)
        plt.subplot(122)
        plt.plot(period_hr_r, band_circ_power[0])
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Period (hours)")
        plt.axvline(x=24, color='r', linestyle='--', label='24 hours') 
        plt.ylabel("Power Spectral Density")
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.suptitle(f"Circadian Power Spectrum - {sub} {ch} {band_vals[0]}")
        plt.tight_layout()
        #pdf_.savefig(f"circadian_power_{sub}_{ch}.pdf")
        pdf_.savefig(plt.gcf())
        plt.close()
    pdf_.close()

    if SHUFFLE:
        pkl_path = f"circ_power_shuffled/circ_power_{subject}_shuffled.pkl"
    else:
        pkl_path = f"circ_power/circ_power_{subject}.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(d_sub, f)

if __name__ == "__main__":
    #run_sub(subjects[0], SHUFFLE=True)  # test run
    Parallel(n_jobs=40)(
        delayed(run_sub)(subject, SHUFFLE=shuffle_) for subject in subjects for shuffle_ in [False, True]
    )

# nohup python compute_circadian_power.py > compute_circadian_power.log 2>&1 &
