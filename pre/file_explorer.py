import os
import uuid
from neo.io import BlackrockIO
import mne
from matplotlib import pyplot as plt
import datetime
import numpy as np
import tqdm_joblib
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm


def read_ns3_file(ns3_file_path):
    reader = BlackrockIO(filename=ns3_file_path)

    blk = reader.read_block()

    seg = blk.segments[0]
    #analogsignals = seg.analogsignals
    #spiketrains = seg.spiketrains
    dt = blk.segments[0].rec_datetime

    fs = float(blk.segments[0].analogsignals[0].sampling_rate)
    times = np.array(blk.segments[0].analogsignals[0].times)
    channels = list(blk.segments[0].analogsignals[0].array_annotations["channel_names"])
    time_elapsed_times = times[-1] - times[0]
    time_elapsed_data = blk.segments[0].analogsignals[0].magnitude.shape[0] / fs
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} Reading {os.path.basename(ns3_file_path)} time elapsed times: {time_elapsed_times}s, time elapsed data: {time_elapsed_data}s")

    info = mne.create_info(ch_names=channels, sfreq=fs, ch_types="seeg")
    dt = dt.astimezone(datetime.timezone.utc)
    info.set_meas_date(dt)
    data = blk.segments[0].analogsignals[0].magnitude.T * 1e-6  # convert to Volts

    del reader, blk, seg

    if fs == 2000:
        data = data[:, ::5] # TODO
    else:
        raise ValueError(f"Unexpected sampling rate: {fs}")
    raw = mne.io.RawArray(data, info, verbose=False)
    del data
    #raw.resample(400, npad="auto")
    return raw, times

def process_file(data_range_path, ns3_file, path_output):
    #print(f"Reading {ns3_file}")
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time } Processing {ns3_file}")
        ns3_file_path = os.path.join(data_range_path, ns3_file)
        raw, times = read_ns3_file(ns3_file_path)
        
        dt = raw.info["meas_date"]
        timestamp_str = dt.strftime("%Y%m%dT%H%M%S")
        for i, ch in enumerate(raw.ch_names):
            channel_data = raw.get_data(picks=[ch]).flatten().astype(np.float16)
            npy_filename = f"{subject}_{timestamp_str}_{ch}.npy"
            npy_filepath = os.path.join(path_output, npy_filename)
            np.save(npy_filepath, channel_data)#
    except Exception as e:
        # write to log file
        # save an empty txt file with the error message
        # loguru logging
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} Error processing {ns3_file}: {e}")

PATH_DATA = "/mnt/datalake/data/emu"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data"


# call with nohup uv run file_explorer.py > logs/file_explorer.log 2>&1 &
# and check with `ps aux | grep file_explorer.py` the process running

if __name__ == "__main__":

    subjects = [s for s in os.listdir(PATH_DATA) if s.startswith("YF")]
    for subject in subjects[5:]:
        
        #subject = subjects[0]
        subject_path = os.path.join(PATH_DATA, subject)
        sub_path_out = os.path.join(PATH_OUT, subject)
        if not os.path.exists(sub_path_out):
            os.makedirs(sub_path_out)

        subject_path = os.path.join(PATH_DATA, subject)
        subject_path_data = os.path.join(subject_path, "DATA")

        data_ranges = [f for f in os.listdir(subject_path_data) if f.startswith("2")]

        for data_range in tqdm(data_ranges, desc="Data Ranges subject " + subject):

            data_range_path = os.path.join(subject_path_data, data_range)

            l_ns3 = [f for f in os.listdir(data_range_path) if f.endswith("ns3")]
            for ns3 in l_ns3: 
                _ = process_file(data_range_path, ns3, sub_path_out)

            #Parallel(n_jobs=2)(delayed(process_file)(data_range_path, ns3_file, sub_path_out) for ns3_file in l_ns3)
