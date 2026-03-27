import numpy as np
import pandas as pd
from pathlib import Path
from joblib import Parallel, delayed
from collections import defaultdict
from tqdm import tqdm

PATH_NPY = Path("chunks_out_fixed")
OUT_PATH = Path("foundation_model_prep")
OUT_PATH.mkdir(exist_ok=True)

df_elecs = pd.read_csv("CSVs/combined_electrodes_MNI152.csv")

def parse_file(f: Path):
    subject = f.parts[-3]
    ch = f.parts[-2][:-4]
    time_ = f.stem[-15:]  # YYYYMMDD-HHMMSS
    return subject, ch, time_, f


#for subject_dir in PATH_NPY.iterdir():
def process_sub(subject_dir: Path):
    # if not subject_dir.is_dir():
    #     continue

    subject = subject_dir.name
    sub_str = subject[:3]

    print(f"Processing subject {subject}")

    # ---------- 1. Load electrode coords once ----------
    df_sub = df_elecs[df_elecs["Subject"] == sub_str]

    coord_lookup = {
        row.Label: np.array([row.MNI152_x, row.MNI152_y, row.MNI152_z])
        for row in df_sub.itertuples()
    }

    # ---------- 2. Parse & group files by time ----------
    files_by_time = defaultdict(list)

    for f in subject_dir.rglob("*.npy"):
        _, ch, time_, fpath = parse_file(f)
        files_by_time[time_].append((ch, fpath))

    unique_times = sorted(files_by_time.keys())

    # ---------- 3. Worker ----------
    def save_time(time_):
        entries = files_by_time[time_]

        data_list = []
        coord_rows = []

        for ch, fpath in entries:
            #data_list.append(np.load(fpath, mmap_mode="r").shape[0],)
            #data_list.append(np.load(fpath))

            if ch in coord_lookup:
                x, y, z = coord_lookup[ch]
            else:
                print(f"Warning: No electrode info for subject {subject} channel {ch}")
                x = y = z = np.nan

            coord_rows.append({
                "Subject": sub_str,
                "Label": ch,
                "MNI152_x": x,
                "MNI152_y": y,
                "MNI152_z": z,
            })

        #arr = np.stack(data_list, axis=0)
        #arr_shape_l = [d.shape for d in data_list]
        coord_df = pd.DataFrame(coord_rows)

        # compare the shape for each element in arr_shape_l with coord_df shape
        if len(entries) != coord_df.shape[0]:
            print(f"Error: shape mismatch {subject} {time_}")
            return

        # np.save(OUT_PATH / f"{subject}_{time_}_data.npy", arr)
        coord_df.to_csv(OUT_PATH / f"{subject}_{time_}_coords.csv", index=False)

    # ---------- 4. Parallel execution ----------
    for time in tqdm(unique_times):
        save_time(time)
    # save_time(unique_times[0])  # for debugging
    # Parallel(n_jobs=-1, backend="loky")(
    #     delayed(save_time)(time_) for time_ in unique_times
    # )

    print(f"Finished subject {subject}")

if __name__ == "__main__":
    # use joblib 
    # Parallel(n_jobs=10)(
    #     delayed(process_sub)(subject_dir)
    #     for subject_dir in PATH_NPY.iterdir()
    #     if subject_dir.is_dir()
    # )

    # 1. delete all .csv files in OUT_PATH
    for f in OUT_PATH.glob("*.csv"):
        f.unlink()

    for subject_dir in PATH_NPY.iterdir():
        #if "YFF" not in subject_dir.name:
        #    continue
        if subject_dir.is_dir():
            process_sub(subject_dir)