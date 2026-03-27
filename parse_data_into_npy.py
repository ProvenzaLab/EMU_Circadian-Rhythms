#!/usr/bin/env python3
import os
import datetime
import numpy as np
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm
import pandas as pd
from time import time
import sys

import mne
from neo.io import BlackrockIO
from neo.rawio import BlackrockRawIO
import brpylib

# =========================
# Config
# =========================
PATH_DATA = "/mnt/datalake/data/emu"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data_250Hz_new"
N_JOBS = 4  # joblib workers

os.makedirs(PATH_OUT, exist_ok=True)


# nohup python parse_data_into_npy.py > main.out 2>&1 &
# tree -h | head -n 500

# =========================
# NS3 helpers
# =========================
def read_ns3_file(ns3_file_path: str) -> mne.io.Raw:
    """
    Load full NS3 into MNE Raw and resample to 400 Hz.
    """
    reader = BlackrockIO(filename=ns3_file_path)
    blk = reader.read_block()
    seg = blk.segments[0]
    analogsignals = seg.analogsignals
    dt = seg.rec_datetime

    analogsignal = analogsignals[0]
    fs = float(analogsignal.sampling_rate)
    voltages = analogsignal.magnitude
    channels = list(analogsignal.array_annotations["channel_names"])

    info = mne.create_info(ch_names=channels, sfreq=fs, ch_types="seeg")
    dt = dt.astimezone(datetime.timezone.utc)
    info.set_meas_date(dt)
    data = voltages.T * 1e-6  * 4 # convert to Volts, times 4 is important bc of neo brpylib conversion
    data = data.astype(np.float32)
    raw = mne.io.RawArray(data, info, verbose=False)
    raw.resample(250, npad="auto", n_jobs=N_JOBS)
    return raw


def ns3_header(ns3_file_path: str, LIMIT_DURATION_MIN: int = None, read_ns3=True):
    """
    Lightweight header read to get (timestamp_str_UTC, channel_names) without loading all data.
    Uses BlackrockRawIO (header only) and a tiny lazy read to get rec_datetime if needed.
    """
    r = BlackrockRawIO(filename=ns3_file_path)
    r.parse_header()

    # Channel names from header
    chan_info = r.header["signal_channels"]
    try:
        if read_ns3:
            ch_names = [c[1] for c in chan_info]  # many neo versions store (id, name, ...)
        else:
            ch_names = [c[0] for c in chan_info]
    except Exception:
        ch_names = [c["name"] for c in chan_info]

    # rec_datetime usually not exposed in RawIO header; get via lazy high-level read
    io = BlackrockIO(filename=ns3_file_path)
    blk = io.read_block(lazy=True)  # lazy -> doesn't load arrays
    dt = blk.segments[0].rec_datetime
    dt = dt.astimezone(datetime.timezone.utc)

    sampling_rate = r.get_signal_sampling_rate(0)
    samples = r.get_signal_size(0, 0, 0)
    duration_min = samples / sampling_rate / 60

    
    if LIMIT_DURATION_MIN is not None:
        if duration_min > LIMIT_DURATION_MIN:
            return None, None


    #timestamp_str = dt.strftime("%Y%m%dT%H%M%S")
    return dt, ch_names

def process_file(data_range_path: str, ns3_file: str, path_output: str, subject: str, read_ns3=True):

    ns3_file_path = os.path.join(data_range_path, ns3_file)

    try:
        # Quick header probe: timestamp + channels
        timestamp_str, ch_names = ns3_header(ns3_file_path, read_ns3=read_ns3)
        if timestamp_str is None:
           print(f"Skip (too long): {ns3_file_path}")
           return
        str_dt = timestamp_str.strftime("%Y%m%dT%H%M%S")
        out_filename = f"{subject}_{str_dt}_data.npy"
        if os.path.exists(os.path.join(path_output, out_filename)):
            print(f"Skip (exists): {ns3_file_path}")
            return

        print(f"Processing: {ns3_file_path}")
        raw = read_ns3_file(ns3_file_path)
        dt = raw.info["meas_date"]
        str_dt = dt.strftime("%Y%m%dT%H%M%S")

        data = raw.get_data().astype(np.float16)
        # shape is (n_channels, n_times)

        print(f"Processed: {ns3_file_path}")

        np.save(os.path.join(path_output, f"{subject}_{str_dt}_data.npy"), data)

        ch_names = list(raw.ch_names)
        # same the ch_names as csv
        df_ch = pd.DataFrame({"channel_names": ch_names})
        df_ch.to_csv(os.path.join(path_output, f"{subject}_{str_dt}_channels.csv"), index=False)

    except Exception as e:
        try:
            # Goes to both main & error log; includes traceback
            print(f"Error processing file using neo {ns3_file_path}: {e}")
            # try to open using brpylib
            nsx_file = brpylib.NsxFile(ns3_file_path) 
            data = nsx_file.getdata()
            data_duration_s = data["data_headers"][0]["data_time_s"]
            data_arr = data["data"][0]
            fs = data["samp_per_s"]
            df_elec = pd.DataFrame(nsx_file.extended_headers)
            # units: df_elec["Units"].unique()
            channels = df_elec["ElectrodeLabel"].tolist()
            meas_dat = nsx_file.basic_header["TimeOrigin"]
            str_dt = meas_dat.strftime("%Y%m%dT%H%M%S")

            raw = mne.io.RawArray(data_arr * 1e-6, mne.create_info(channels, fs, ch_types="seeg"))
            raw.resample(250, npad="auto", n_jobs=6)
            data = raw.get_data().astype(np.float16)
        
            np.save(os.path.join(path_output, f"{subject}_{str_dt}_data.npy"), data)
            df_ch = pd.DataFrame({"channel_names": channels})
            df_ch.to_csv(os.path.join(path_output, f"{subject}_{str_dt}_channels.csv"), index=False)

            print(f"Processed with brpylib: {ns3_file_path}")
        except Exception as e2:
            print(f"Error processing file using brpylib {ns3_file_path}: {e2}")
            return


if __name__ == "__main__":

    subjects = [s for s in os.listdir(PATH_DATA) if s.startswith("YF")]
    ns5_files_to_proces = []
    # get all files ending with ns3 in folders, sub-folders, and sub-sub-folders
    PASS_NS3_CHECK = False
    #for subject in subjects:
    subject = subjects[int(sys.argv[1])]
    subject_path = os.path.join(PATH_DATA, subject)
    sub_path_out = os.path.join(PATH_OUT, subject)
    os.makedirs(sub_path_out, exist_ok=True)

    subject_path_data = os.path.join(subject_path, "DATA")
    #if not os.path.isdir(subject_path_data):
    #    print(f"Missing DATA folder for subject {subject}: {subject_path_data}")
    #    continue

    data_ranges = [f for f in os.listdir(subject_path_data) if f.startswith("2")]
    for data_range in data_ranges:#, desc=f"Data Ranges [{subject}]"):
        data_range_path = os.path.join(subject_path_data, data_range)
        if not os.path.isdir(data_range_path):
            print(f"Not a directory: {data_range_path}")
            continue

        l_ns3 = [f for f in os.listdir(data_range_path) if f.endswith("ns3")]
        if not l_ns3:
            print(f"No NS3 files in {data_range_path}")
            l_ns5 = [f for f in os.listdir(data_range_path) if f.endswith("ns5")]
            if l_ns5:
                # add every elemt in l_ns5 to a list and save as a single npy file
                for ns5_file in l_ns5:
                    ns5_files_to_proces.append((data_range_path, ns5_file, sub_path_out, subject))
                
                for ns5_file in l_ns5:
                    process_file(data_range_path, ns5_file, sub_path_out, subject, read_ns3=False)
            continue
        
        if PASS_NS3_CHECK is True:
            continue
        for l_ns3_file in l_ns3:
            process_file(data_range_path, l_ns3_file, sub_path_out, subject)

    #print(f"Completed subject: {subject}")

#df_ns5 = pd.DataFrame(ns5_files_to_proces, columns=["data_range_path", "ns5_file", "sub_path_out", "subject"])
#df_ns5.to_csv("ns5_files_to_process.csv", index=False)

# nohup python parse_data_into_npy.py > main.out 2>&1 &
