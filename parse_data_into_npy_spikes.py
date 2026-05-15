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
from scipy import signal

try:
    profile
except NameError:
    def profile(func):
        return func

# =========================
# Config
# =========================
PATH_DATA = "/mnt/datalake/data/emu"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data_250Hz_spikes"
N_JOBS = 16  # joblib workers

os.makedirs(PATH_OUT, exist_ok=True)


# nohup python parse_data_into_npy.py > main.out 2>&1 &
# tree -h | head -n 500

# =========================
# NS5 helpers
# =========================
@profile
def read_ns5_file(ns5_file_path: str):
    """
    Load full NS5 into MNE Raw, apply bandpass filters:
    - 300-1000 Hz for spiking band power
    - 300-7000 Hz for MUA threshold crossings (4 * MAD).

    Outputs are sampled at 250 Hz:
    - band_magnitude_ds: anti-aliased decimated spiking-band magnitude
    - mua_counts: number of threshold-crossing samples in each 250 Hz time bin
    """
    reader = BlackrockIO(filename=ns5_file_path)
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

    # 300-1000 Hz bandpass for spiking band power
    raw_bp_spike = raw.copy().filter(l_freq=300.0, h_freq=1000.0, n_jobs=N_JOBS, verbose=False)
    bp_spike_data = raw_bp_spike.get_data().astype(np.float32)  # (n_channels, n_times)

    # Magnitude in spiking band
    band_magnitude = np.abs(bp_spike_data).astype(np.float32)

    # 300-7000 Hz bandpass for MUA (multi-unit activity)
    raw_bp_mua = raw.copy().filter(l_freq=300.0, h_freq=7000.0, n_jobs=N_JOBS, verbose=False)
    bp_mua_data = raw_bp_mua.get_data().astype(np.float32)  # (n_channels, n_times)

    # MUA by threshold crossing using 4 * MAD (binary output)
    med = np.median(bp_mua_data, axis=1, keepdims=True)
    mad = np.median(np.abs(bp_mua_data - med), axis=1, keepdims=True)
    threshold = 4.0 * mad
    mua_binary = (np.abs(bp_mua_data) >= threshold).astype(np.uint8)

    # Downsample band magnitude to 250 Hz with anti-aliasing filter
    downsample_factor = int(fs / 250.0)
    band_magnitude_ds = signal.decimate(band_magnitude, downsample_factor, axis=1, zero_phase=True)

    # For MUA, store counts per 250 Hz bin (not decimated binary values)
    bin_starts = np.arange(0, mua_binary.shape[1], downsample_factor)
    mua_counts = np.add.reduceat(mua_binary, bin_starts, axis=1).astype(np.uint16)

    return band_magnitude_ds, mua_counts, dt, channels


@profile
def ns5_header(ns5_file_path: str, LIMIT_DURATION_MIN: int = None):
    """
    Lightweight header read to get (timestamp_str_UTC, channel_names) without loading all data.
    Uses BlackrockRawIO (header only) and a tiny lazy read to get rec_datetime if needed.
    """
    r = BlackrockRawIO(filename=ns5_file_path)
    r.parse_header()

    # Channel names from header
    chan_info = r.header["signal_channels"]
    try:
        ch_names = [c[1] for c in chan_info]  # many neo versions store (id, name, ...)
    except Exception:
        ch_names = [c["name"] for c in chan_info]

    # rec_datetime usually not exposed in RawIO header; get via lazy high-level read
    io = BlackrockIO(filename=ns5_file_path)
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

@profile
def process_file(data_range_path: str, ns5_file: str, path_output: str, subject: str):

    ns5_file_path = os.path.join(data_range_path, ns5_file)

    try:
        # Quick header probe: timestamp + channels
        timestamp_str, ch_names = ns5_header(ns5_file_path)
        if timestamp_str is None:
           print(f"Skip (too long): {ns5_file_path}")
           return
        str_dt = timestamp_str.strftime("%Y%m%dT%H%M%S")
        out_data_filename = f"{subject}_{str_dt}_sbp_mua.npy"
        out_channels_filename = f"{subject}_{str_dt}_channels.csv"
        out_data_path = os.path.join(path_output, out_data_filename)
        out_channels_path = os.path.join(path_output, out_channels_filename)

        if os.path.exists(out_data_path) and os.path.exists(out_channels_path):
            print(f"Skip (exists): {ns5_file_path}")
            return

        print(f"Processing: {ns5_file_path}")
        band_magnitude, mua_counts, dt, ch_names = read_ns5_file(ns5_file_path)
        str_dt = dt.strftime("%Y%m%dT%H%M%S")

        print(f"Processed: {ns5_file_path}")

        # Combine outputs into single array: [band_magnitude, mua_counts]
        combined_data = np.stack([band_magnitude.astype(np.float16), mua_counts.astype(np.float16)])
        np.save(os.path.join(path_output, f"{subject}_{str_dt}_sbp_mua.npy"), combined_data)

        # save the ch_names as csv
        df_ch = pd.DataFrame({"channel_names": ch_names})
        df_ch.to_csv(os.path.join(path_output, f"{subject}_{str_dt}_channels.csv"), index=False)

    except Exception as e:
        try:
            # Goes to both main & error log; includes traceback
            print(f"Error processing file using neo {ns5_file_path}: {e}")
            # try to open using brpylib
            nsx_file = brpylib.NsxFile(ns5_file_path) 
            data = nsx_file.getdata()
            data_duration_s = data["data_headers"][0]["data_time_s"]
            data_arr = data["data"][0]
            fs = data["samp_per_s"]
            df_elec = pd.DataFrame(nsx_file.extended_headers)
            # units: df_elec["Units"].unique()
            channels = df_elec["ElectrodeLabel"].tolist()
            meas_dat = nsx_file.basic_header["TimeOrigin"]
            str_dt = meas_dat.strftime("%Y%m%dT%H%M%S")

            raw = mne.io.RawArray((data_arr * 1e-6).astype(np.float32), mne.create_info(channels, fs, ch_types="seeg"), verbose=False)
            
            # 300-1000 Hz bandpass for spiking band power
            raw_bp_spike = raw.copy().filter(l_freq=300.0, h_freq=1000.0, n_jobs=N_JOBS, verbose=False)
            bp_spike_data = raw_bp_spike.get_data().astype(np.float32)
            band_magnitude = np.abs(bp_spike_data).astype(np.float32)
            
            # 300-7000 Hz bandpass for MUA (multi-unit activity)
            raw_bp_mua = raw.copy().filter(l_freq=300.0, h_freq=7000.0, n_jobs=N_JOBS, verbose=False)
            bp_mua_data = raw_bp_mua.get_data().astype(np.float32)
            med = np.median(bp_mua_data, axis=1, keepdims=True)
            mad = np.median(np.abs(bp_mua_data - med), axis=1, keepdims=True)
            threshold = 4.0 * mad
            mua_binary = (np.abs(bp_mua_data) >= threshold).astype(np.uint8)

            # Downsample band magnitude to 250 Hz with anti-aliasing filter
            downsample_factor = int(fs / 250.0)
            band_magnitude = signal.decimate(band_magnitude, downsample_factor, axis=1, zero_phase=True).astype(np.float16)

            # For MUA, store counts per 250 Hz bin (not decimated binary values)
            bin_starts = np.arange(0, mua_binary.shape[1], downsample_factor)
            mua_counts = np.add.reduceat(mua_binary, bin_starts, axis=1).astype(np.float16)

            # Combine outputs into single array: [band_magnitude, mua_counts]
            combined_data = np.stack([band_magnitude, mua_counts])
            np.save(os.path.join(path_output, f"{subject}_{str_dt}_sbp_mua.npy"), combined_data)
            df_ch = pd.DataFrame({"channel_names": channels})
            df_ch.to_csv(os.path.join(path_output, f"{subject}_{str_dt}_channels.csv"), index=False)

            print(f"Processed with brpylib: {ns5_file_path}")
        except Exception as e2:
            print(f"Error processing file using brpylib {ns5_file_path}: {e2}")
            return


if __name__ == "__main__":

    print(f"Available CPU cores: {os.cpu_count()}")

    subjects = [s for s in os.listdir(PATH_DATA) if s.startswith("YF")]

    #subjects_left = ["YFU", "YFT", "YFS", "YFR", "YFQ", "YFP", "YFL", "YFD", "YFC", "YFB", "YFA", "YFV", ]
    
    # check for each subject in subjects if at least one subjects_left is in the subject name
    #subjects = [s for s in subjects if any(sub in s for sub in subjects_left)]
    
    ns5_files_to_proces = []
    # get all files ending with ns3 in folders, sub-folders, and sub-sub-folders
    PASS_NS3_CHECK = False
    #for subject in subjects:
    sys_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if sys_arg is not None and (sys_arg < 0 or sys_arg >= len(subjects)):
        print(f"Subject index out of range: {sys_arg} for left subjects")
        exit(1)
    subject = subjects[sys_arg] if sys_arg is not None else subjects[0]
    subject_path = os.path.join(PATH_DATA, subject)
    sub_path_out = os.path.join(PATH_OUT, subject)
    os.makedirs(sub_path_out, exist_ok=True)

    subject_path_data = os.path.join(subject_path, "DATA")
    #if not os.path.isdir(subject_path_data):
    #    print(f"Missing DATA folder for subject {subject}: {subject_path_data}")
    #    continue
    stop = False

    data_ranges = [f for f in os.listdir(subject_path_data) if f.startswith("2")]
    for data_range in data_ranges[::-1]:#, desc=f"Data Ranges [{subject}]"):
        data_range_path = os.path.join(subject_path_data, data_range)
        if not os.path.isdir(data_range_path):
            print(f"Not a directory: {data_range_path}")
            continue

        l_ns5 = [f for f in os.listdir(data_range_path) if f.endswith("ns5") and f.startswith("NSP2")]
        if not l_ns5:
            print(f"No NS5 files in {data_range_path}")
            continue

        for l_ns5_file in l_ns5:
            process_file(data_range_path, l_ns5_file, sub_path_out, subject)

        if stop:
            break
    

