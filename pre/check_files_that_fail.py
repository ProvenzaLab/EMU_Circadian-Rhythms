#!/usr/bin/env python3
import os
import datetime
import numpy as np
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from tqdm import tqdm
import pandas as pd
from time import time

import mne
from neo.io import BlackrockIO
from neo.rawio import BlackrockRawIO
import brpylib

ns3_file_path = "/mnt/datalake/data/emu/YFBDatafile/DATA/20240507-140543/NSP1-20240507-140543-004.ns3"
ns3_file_path = "/mnt/datalake/data/emu/YFFDatafile/DATA/20240826-135742/NSP1-20240826-135742-084.ns3"
ns3_file_path = "/mnt/datalake/data/emu/YFFDatafile/DATA/20240827-083543/NSP1-20240827-083543-001.ns3"
io = BlackrockIO(filename=ns3_file_path)
blk = io.read_block()
seg = blk.segments[0]
analogsignals = seg.analogsignals
dt = seg.rec_datetime

analogsignal = analogsignals[0]
fs = float(analogsignal.sampling_rate)
voltages = analogsignal.magnitude
channels_YFF_wrong = list(analogsignal.array_annotations["channel_names"])

ns3_file_path = "/mnt/datalake/data/emu/YFEDatafile/DATA/20240816-153949/NSP1-20240816-153949-006.ns3"
io = BlackrockIO(filename=ns3_file_path)
blk = io.read_block()
seg = blk.segments[0]
analogsignals = seg.analogsignals
dt = seg.rec_datetime

analogsignal = analogsignals[0]
fs = float(analogsignal.sampling_rate)
voltages = analogsignal.magnitude
channels_YFE = list(analogsignal.array_annotations["channel_names"])

ns3_file_path = "/mnt/datalake/data/emu/YFFDatafile/DATA/20240819-200938/NSP1-20240819-200938-066.ns3"
io = BlackrockIO(filename=ns3_file_path)
blk = io.read_block()
seg = blk.segments[0]
analogsignals = seg.analogsignals
dt = seg.rec_datetime

analogsignal_Right = analogsignals[0]
fs = float(analogsignal_Right.sampling_rate)
voltages = analogsignal_Right.magnitude
channels_YFF_right = list(analogsignal_Right.array_annotations["channel_names"])


df = pd.DataFrame({"YFF": channels_YFF_wrong, "YFE": channels_YFE, "YFF_correct": channels_YFF_right})