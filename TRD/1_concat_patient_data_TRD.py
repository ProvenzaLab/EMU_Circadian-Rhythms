import pandas as pd
import os
os.chdir("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms") #for changing what os points to, so that it works even though I'm running from TRD folder
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed

PATH_DATA = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data_250Hz"
#PATH_electrodes = "/mnt/datalake/data/emu/"
patients = [f for f in os.listdir(PATH_DATA) if f.startswith("DBS")]

def read_npy_file_safe(npy_):
    try:
        read_npy_file(npy_)
    except Exception as e:
        print('error')

def read_npy_file(npy_):
    data = np.load(os.path.join(PATH_DATA, patient, npy_))
    ch_ = []
    times_ = []
    for ch in df_chs['channel_names'].unique():
        
        df_ch_sub = df_chs[(df_chs['channel_names'] == ch) & (df_chs['rec_file'] == npy_.split("_")[1])]
        if df_ch_sub.empty:
            continue
        ch_index = df_ch_sub['index_'].values[0]
        ch_data = data[ch_index, :]
        ch_data.shape
        time_vec = np.arange(ch_data.shape[0]) / 250.0
        start_time = pd.to_datetime(df_ch_sub['rec_file'].values[0]) # format '20240423T121303'
        time_vec = start_time + pd.to_timedelta(time_vec, unit='s')

        df_ = pd.DataFrame({"time": time_vec, "value": ch_data})
        # get 10 second chunks
        chunks = []
        chunk_size = 60 * 250 * 10  # 10 min at 250 Hz
        for i in range(0, df_.shape[0], chunk_size):
            # if not complete chunk, skip
            if i + chunk_size - 2000 > df_.shape[0] :  # I allow that 2000 samples might be missing within the 10 min
                # that equates to 8 seconds
                continue
            chunk = df_.iloc[i:i+chunk_size]
            path_out_patient_ch = os.path.join(path_out_patient, ch)
            if not os.path.exists(path_out_patient_ch):
                os.makedirs(path_out_patient_ch, exist_ok=True)
            time_ = chunk['time'].values[0]
            time_str = pd.to_datetime(time_).strftime("%Y%m%d-%H%M%S")
            path_out = os.path.join(path_out_patient_ch, f"{patient}_{ch}_{time_str}.npy")
            np.save(path_out, chunk['value'].values)

if __name__ == "__main__":

    elec_paths = "/mnt/projectworlds/EMU-18112/ElectrodeLabelsROIs/+electrodes+csvs"

    for patient in patients[::-1]:
        #patient = "YFADatafile"
        print(f"Processing patient: {patient}")

        npy_files = [f for f in os.listdir(os.path.join(PATH_DATA, patient)) if f.endswith("_data.npy")]
        csv_files = [f for f in os.listdir(os.path.join(PATH_DATA, patient)) if f.endswith("_channels.csv")]
    
        if not os.path.exists(f"meta_joined/{patient}_coords_ns3_mapped.csv"):
            patient_sub = patient[:3]
            if patient_sub != "YFU":
                l_ = [l for l in os.listdir(elec_paths) if patient_sub in l]
                if not l_:
                    print(f"Missing electrode file for patient {patient}, skipping.")
                    continue
                df_elecsub = pd.read_csv(os.path.join(elec_paths, l_[0]))
            else:
                df_elecsub = pd.read_csv("/mnt/projectworlds/EMU-18112/YFU_Datafile/IMG/YFU-electrodes_v2025+.csv") #must be a different placement of this foler for YFU
        
            chs = []
            for csv_ in csv_files:
                df_ch = pd.read_csv(os.path.join(PATH_DATA, patient, csv_))
                df_ch["rec_file"] = csv_.split("_")[1]
                df_ch["sub"] = csv_.split("_")[0]
                df_ch["index_"] = np.arange(df_ch.shape[0])
                df_ch["Label"] = df_ch["channel_names"].apply(lambda x: x.split("-")[0] if "-" in x else x)
                df_ch = df_ch.merge(df_elecsub[["Label", "MNI305_x", "MNI305_y", "MNI305_z"]], on="Label", how="left")
                chs.append(df_ch)
            df_chs = pd.concat(chs, axis=0)
            df_chs.to_csv(f"meta_joined/{patient}_coords_ns3_mapped.csv", index=False)
        else:
            df_chs = pd.read_csv(f"meta_joined/{patient}_coords_ns3_mapped.csv")

        path_out_patient = f"chunks_out_fixed/{patient}/"
        if not os.path.exists(path_out_patient):
            os.makedirs(path_out_patient, exist_ok=True)
 
        Parallel(n_jobs=20)(
            delayed(read_npy_file_safe)(npy_) for npy_ in tqdm(npy_files)
        )

# run this using
# nohup python concat_patient_data.py > concat_patient_data.log 2>&1 &

#     # from matplotlib import pyplot as plt
#     # plt.figure()
#     # df_["value"].iloc[:5*250].plot()
#     # plt.savefig(f"test.png")
#     df = pd.concat(ch_, axis=0)
#     # set index to time
#     df.set_index('time', inplace=True)
#     df = df.sort_index()
#     # resample to 1 second
#     df_resampled = df.resample('4ms').mean()
    
#     data_ch_concat = np.concatenate(ch_, axis=0)
#     times_vec = np.concatenate(times_, axis=0)
# f1 = np.load(os.path.join(PATH_DATA, patient, npy_files[0]))
# c1 = pd.read_csv(os.path.join(PATH_DATA, patient, csv_files[0]))
# print(f"Data shape: {f1.shape}")
# print(f"Channels: {c1.shape[0]}")
# dt = npy_files[0].split("_")[1]

# size_mb = f1.nbytes / (1024 ** 2)

# # one file around 50 MB: 1208 files. = 60 GB per patint roughly
# print(f"File date-time: {dt}, size: {size_mb:.2f} MB")

# ok, I want to save those with continuous time; 
# would a simple concatenation work and then resample

# I want to save a npy array with shape 

# given that we pass 2 days of recordings with 250 Hz
# 2 days = 48 hours = 48 * 3600 seconds = 172800 seconds
# at 250 Hz = 172800 * 250 = 43200000 time points
# 43 mio samples * 4 byte (float32) = 172800000 byte = 172.8 MB per channel
# would theoreticall fit in RAM
# best would be to represent as individual channels; probably also after for masking...

# note that the number of operations would be high, the upper would be a single sample
# how to train this thing using contrastive learning?
# separate loss functions for different times?
# encoders would need to simultaneously be trained

# ok it would require a lot of computations
