import os
import uuid
from neo.io import BlackrockIO
import mne
from matplotlib import pyplot as plt
import datetime
import numpy as np
import tqdm_joblib
# from nwb_writer import MNEtoNWBWriter
# from pynwb import NWBHDF5IO, NWBFile, TimeSeries
# from pynwb.file import Subject
# from hdmf.backends.hdf5.h5_utils import H5DataIO
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm


def read_ns3_file(ns3_file_path):
    reader = BlackrockIO(filename=ns3_file_path)

    blk = reader.read_block()

    seg = blk.segments[0]
    analogsignals = seg.analogsignals
    spiketrains = seg.spiketrains
    dt = seg.rec_datetime

    analogsignal = analogsignals[0]

    # there are two arrays in analogsignals, [1] is
    # array(['Photodiode', 'Audio', 'RoomMic1', 'RoomMic2', 'StimSync',
    #       'RPupil', 'Strobe', 'LTC', 'PS4_button', 'PS4_audio',
    #       'RecordingSync'], dtype='<U13')
    # with 30 kHz 

    # I guess that the the times are relative to the fileonset

    fs = float(analogsignal.sampling_rate)
    times = np.array(analogsignal.times)   # I don't really sample differences with np.unique(np.diff(times))
    voltages = analogsignal.magnitude
    channels = list(analogsignal.array_annotations["channel_names"])

    # create mne raw object
    info = mne.create_info(ch_names=channels, sfreq=fs, ch_types="seeg")
    dt = dt.astimezone(datetime.timezone.utc)
    info.set_meas_date(dt)
    data = voltages.T * 1e-6  # convert to Volts
    raw = mne.io.RawArray(data, info, verbose=False)
    raw.resample(400, npad="auto")

    return raw

def process_file(data_range_path, ns3_file, path_output):
    #print(f"Reading {ns3_file}")
    ns3_file_path = os.path.join(data_range_path, ns3_file)
    raw = read_ns3_file(ns3_file_path)
    # for each channel in raw, save a npy file with name SUBJECT_TIME_CHANNEL.npy
    # the time comes from the raw.info['meas_date']
    dt = raw.info["meas_date"]
    timestamp_str = dt.strftime("%Y%m%dT%H%M%S")
    for i, ch in enumerate(raw.ch_names):
        channel_data = raw.get_data(picks=[ch]).flatten().astype(np.float16)
        npy_filename = f"{subject}_{timestamp_str}_{ch}.npy"
        npy_filepath = os.path.join(path_output, npy_filename)
        np.save(npy_filepath, channel_data)

PATH_DATA = "/mnt/datalake/data/emu"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data"


# call with nohup uv run file_explorer.py > logs/file_explorer.log 2>&1 &
# and check with `ps aux | grep file_explorer.py` the process running

if __name__ == "__main__":

    subjects = [s for s in os.listdir(PATH_DATA) if s.startswith("YF")]
    for subject in subjects:
        
        #subject = subjects[0]
        subject_path = os.path.join(PATH_DATA, subject)
        sub_path_out = os.path.join(PATH_OUT, subject)
        if not os.path.exists(sub_path_out):
            os.makedirs(sub_path_out)

        subject_path = os.path.join(PATH_DATA, subject)
        subject_path_data = os.path.join(subject_path, "DATA")

        data_ranges = [f for f in os.listdir(subject_path_data) if f.startswith("2")]

        # read data for one range
        for data_range in tqdm(data_ranges, desc="Data Ranges"):

            data_range_path = os.path.join(subject_path_data, data_range)

            l_ns3 = [f for f in os.listdir(data_range_path) if f.endswith("ns3")]
            #l_ns5 = [f for f in os.listdir(data_range_path) if f.endswith("ns5")]

            # process the ns3 files in parallel
            #_ = process_file(data_range_path, l_ns3[0], sub_path_out)  # process one file to test
            with tqdm_joblib(tqdm(desc="Processing Data items", total=len(l_ns3))) as progress_bar:
                Parallel(n_jobs=12)(delayed(process_file)(data_range_path, ns3_file, sub_path_out) for ns3_file in l_ns3)

#ns3_file_path = os.path.join(data_range_path, l_ns3[0])


#l_raw = []
#for ns3_file in l_ns3:
    

        # plt.plot(channel_data[:1200], label="Original")  # plot every 100th sample to reduce size
        # plt.title(f"{subject} {timestamp_str} {ch}")
        # plt.plot(np.array(channel_data[:1200]).astype(np.float16), label="Reduced")  # plot every 100th sample to reduce size
        # plt.xlabel("Samples")
        # plt.ylabel("Amplitude (V)")
        # plt.legend()
        # plt.savefig(f"figures/{npy_filename}_64.png")
        # plt.close()

# raws_concat = mne.concatenate_raws(l_raw)

# two files are in edf 173 MB
# for this patient I have 83 files, so I expect 7.2 GB ... for one patient
# there are though 188 channels, to it could be 38.3 MB per channel for the whole duration, with fs = 400 Hz

# question is only, how do I separate it...
# potentially also just as npy files; will I need though the other metadata?



# save concatenated raw to edf
# mne.export.export_raw("data/concat_raw.edf", raws_concat, overwrite=True)
# # save as brainvision
# mne.export.export_raw("data/concat_raw.vhdr", raws_concat, fmt="brainvision")

# raw_read = mne.io.read_raw_edf("data/concat_raw.edf", preload=True)

# plt.plot(raws_concat.get_data()[0,::100])
# plt.savefig("figures/raw_data_example_channel.png")

# nwbfile = NWBFile(
#     session_description="test NWB file",
#     identifier=str(uuid.uuid4()),
#     session_start_time=raws_concat.info["meas_date"],
# )

# subject_nwb = Subject(
#     subject_id=subject[:3],
# )
# nwbfile.subject = subject_nwb

# data_compressed = H5DataIO(data=raws_concat.get_data().T, compression=True, chunks=True, maxshape=(None, 2000))

# time_series_with_timestamps = TimeSeries(
#     name="seeg_data",
#     data=data_compressed,
#     timestamps=raws_concat.times,
#     unit="V",
# )

# nwbfile.add_acquisition(time_series_with_timestamps)

# io = NWBHDF5IO("data/basics_tutorial_compressed.nwb", mode="w")
# io.write(nwbfile)
# io.close()



# # plot first 10 seconds of data
# raw.plot(start=0, duration=10, n_channels=30, scalings="auto")
# # save to figures folder
# plt.savefig("figures/raw_data_plot.png")

# # plot the psds
# raw.plot_psd(fmax=200, picks=[channels[0]])
# plt.savefig("figures/raw_data_psd.png")

