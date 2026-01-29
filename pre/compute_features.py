# for each .npy file compute features with a resolution of 1 sec

import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import py_neuromodulation as nm 
from joblib import Parallel, delayed
from tqdm import tqdm
from tqdm_joblib import tqdm_joblib

def process_file(subject_path, file):
    data = np.load(os.path.join(subject_path, file))
    date_ = file.split("_")[1]
    date_dt = datetime.strptime(date_, "%Y%m%dT%H%M%S")
    subject = file.split("_")[0]
    ch_name = file.split("_")[2].replace(".npy", "")

    settings = nm.NMSettings.get_fast_compute()

    channels = nm.utils.set_channels(
        ch_names=[ch_name],
        ch_types=["seeg"],
        reference="default",
        bads=None,
        new_names="default",
        used_types=( "seeg"),
        target_keywords=None,
    )

    settings.features.welch = True
    settings.features.fft = False
    settings.features.bursts = True
    settings.features.sharpwave_analysis = True
    settings.features.fooof = True
    settings.features.raw_hjorth = True
    settings.features.return_raw = True
    settings.features.linelength = True

    settings.welch_settings.return_spectrum = True

    settings.frequency_ranges_hz["delta"] = (1, 4)
    settings.frequency_ranges_hz["low_gamma"] = (35, 55)
    settings.frequency_ranges_hz["high_gamma"] = (65, 180)
    settings.fooof_settings.windowlength_ms = 1000
    settings.fooof_settings.freq_range = (65, 90)

    settings.sampling_rate_features_hz = 1
    settings.segment_length_features_ms = 1000

    settings.preprocessing = ["notch_filter"]
    settings.postprocessing.feature_normalization = False


    stream = nm.Stream(
        sfreq=400,
        channels=channels,
        settings=settings,
        line_noise=60,
        coord_list=None,
        coord_names=None,
        verbose=True,
    )

    PATH_OUT = os.path.join("features", subject)
    if not os.path.exists(PATH_OUT):
        os.makedirs(PATH_OUT)

    features = stream.run(
        data=np.expand_dims(data, axis=0).astype(np.float64),
        out_dir=PATH_OUT,
        experiment_name=file.replace(".npy", ""),
        save_csv=True,
    )

path_ = "data"
subjects = dirs = [d for d in os.listdir(path_) if os.path.isdir(os.path.join(path_, d))]
for subject in subjects:
    subject_path = os.path.join(path_, subject)
    files = [f for f in os.listdir(subject_path) if f.endswith(".npy")]
    
    file = files[0]
    path_check = os.path.join("features", subject,
                              file.replace(".npy", ""), file.replace(".npy", "_FEATURES.csv"))
    if os.path.exists(path_check):
        # remove file from list
        files.remove(file)
    #process_file(subject_path, file)

    with tqdm_joblib(tqdm(desc="Processing Files", total=len(files))) as progress_bar:
        Parallel(n_jobs=12)(delayed(process_file)(subject_path, file) for file in files)
