import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from pathlib import Path
from joblib import Parallel, delayed
import sys

PATH_NPY = "chunks_out_fixed_new"
df_elecs = pd.read_csv("CSVs/combined_electrodes_MNI152.csv")

patients = os.listdir(PATH_NPY)

def get_ch_from_file(file_path):
    parts = file_path.split(os.sep)
    subject = parts[-3]
    ch = parts[-2][:-4]
    time_ = parts[-1][-19:-4]
    return subject, ch, time_

if __name__ == "__main__":
    
    #for subject in patients:

    patient_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    subject = patients[patient_idx]
    print(f"Processing subject: {subject}")   
    chs = os.listdir(os.path.join(PATH_NPY, subject))
    sub_str = subject[:3]
    # get list of all files including subfolders
    files = list(Path(f"chunks_out_fixed_new/{subject}").rglob("*.npy"))
    _, chs, times = zip(*[get_ch_from_file(str(f)) for f in files])

    unique_times = sorted(list(set(times)))
    df_elec_sub = df_elecs.query("Subject == @sub_str")

    # check if output file already exists, if so skip
    for time_ in unique_times:
        output_file = os.path.join("continuous_data_new", f"{subject}_{time_}_data.npy")
        if os.path.exists(output_file):
            print(f"Output file already exists for subject {subject} time {time_}, skipping.")
            continue

    #for time_ in tqdm(unique_times):
    
    def save_time(time_):
        files_ = [f for f in files if time_ in str(f)]
        l_dat = []
        l_coord = []
        for f in files_:
            ch = str(f).split(os.sep)[-2][:-4]
            dat = np.load(str(f))
            l_dat.append(dat)
            l_coord.append(df_elec_sub.query("Label == @ch")[['Subject', 'Label', 'MNI152_x', 'MNI152_y', 'MNI152_z']])

        arr = np.stack(l_dat, axis=0)
        coord_df = pd.concat(l_coord, axis=0).reset_index(drop=True)

        np.save(os.path.join("continuous_data_new", f"{subject}_{time_}_data.npy"), arr)
        #np.save(os.path.join("foundation_model_prep", f"{subject}_{time_}_coords.npy"), coord_df.values)
        # save as csv
        coord_df.to_csv(os.path.join("continuous_data_new", f"{subject}_{time_}_coords.csv"), index=False)
        print(f"Finished subject {subject} time {time_}")
    # use joblib to parallelize
    Parallel(n_jobs=-1)(delayed(save_time)(time_) for time_ in unique_times)
    
    # nohup python combine_npy_for_deeplearning.py > combine_npy_for_deeplearning.log &

    # for ch in tqdm(chs):
    #     ch_str = ch[:-4]
    #     ch_files = os.listdir(os.path.join(PATH_NPY, subject, ch))
    #     ch_coord = df_elecs.query("Subject == @sub_str and Label == @ch_str")[['MNI152_x', 'MNI152_y', 'MNI152_z']]
    #     for ch_idx, ch_f in enumerate(ch_files):
    #         time_ = ch_f[-19:-4]
    #         data = np.load(os.path.join(PATH_NPY, subject, ch, ch_f))
    #         if time_ not in d_:
    #             d_[time_] = {}
    #         if ch_str not in d_[time_]:
    #             d_[time_][ch_str] = {}
    #         d_[time_][ch_str]['data'] = data
    #         if ch_coord.shape[0] > 0:
    #             d_[time_][ch_str]['coord'] = ch_coord.values[0]
    print("here")