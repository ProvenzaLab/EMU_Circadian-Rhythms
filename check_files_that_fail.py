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
io = BlackrockIO(filename=ns3_file_path)
