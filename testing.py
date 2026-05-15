import numpy as np
import matplotlib.pyplot as plt
import os

PLOT_OUT = "f"

# ---- Create fake signal ----
fs = 250
t = np.linspace(0, 10, fs * 5)  # 10 seconds
data = np.sin(2 * np.pi * 2 * t)  # 2 Hz sine wave

# ---- Inject NaNs (small number so interpolation runs) ----
data_with_nans = data.copy()
nan_indices = np.random.choice(len(data), size=50, replace=False)  # 20 NaNs
data_with_nans[nan_indices] = np.nan

# ---- Apply your interpolation logic ----
data_curr = data_with_nans.copy()


nans = np.isnan(data_curr)
not_nans = ~nans

data_curr[nans] = np.interp(
    np.flatnonzero(nans),
    np.flatnonzero(not_nans),
    data_curr[not_nans]
)

# ---- Plot before vs after ----
plt.figure(figsize=(10, 4))

plt.plot(data_curr)
save_name = os.path.join(
PLOT_OUT,"after.png")
plt.savefig(save_name)
plt.close() 

plt.figure(figsize=(10, 4))

plt.plot(data_with_nans)
save_name = os.path.join(
PLOT_OUT,"before.png")
plt.savefig(save_name)
plt.close() 
