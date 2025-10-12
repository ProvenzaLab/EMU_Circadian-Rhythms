import os
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np


PATH_ = "data"
ch_name = "LF2C01-179"
sub = "YFA"
files_to_load = [f for f in os.listdir(PATH_) if f.endswith(f"{ch_name}.npy")]

dates_ = [f.split("_")[1] for f in files_to_load]
dates_ = [datetime.strptime(d, "%Y%m%dT%H%M%S") for d in dates_]
idx_dates_sorted = sorted(range(len(dates_)), key=lambda k: dates_[k])
files_to_load = [files_to_load[i] for i in idx_dates_sorted]
dates_ = [dates_[i] for i in idx_dates_sorted]

plt.figure(figsize=(10, 6))
plt.plot(dates_)
plt.title(f"Files for channel {ch_name}")
plt.savefig("figures/file_dates.png")

# Load and concatenate data
fs = 400
data_list = []
for i, file in enumerate(files_to_load):
    data = np.load(os.path.join(PATH_, file))

    # creating time vector
    times_series = pd.date_range(start=dates_[i], periods=len(data), freq=f"{1000/fs}ms")
    df_ = pd.DataFrame(data={"time": times_series, "ch": ch_name, "sub": sub, "data": data})

df_.plot(x="time", y="data", figsize=(15, 5), title=f"Channel {ch_name} data")
plt.savefig("figures/concatenated_data.png")