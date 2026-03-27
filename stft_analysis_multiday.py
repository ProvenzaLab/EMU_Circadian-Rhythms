from scipy.fft import rfft, rfftfreq
import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
import os
import random

fs = 250
block = fs * 60 * 10 # 10-min block in samples

files = os.listdir("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/continuous_data/")
def plot_file(file_):
    #file = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/continuous_data/YFE_LF2CM04_20240813-053217.000.npy"
    file = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/continuous_data/" + file_
    dat = np.load(file).astype(np.float32)
    dat = np.nan_to_num(dat, copy=True)

    dat = (dat - np.mean(dat)) / np.std(dat)

    n = (len(dat) // block) * block
    x = np.median(dat[:n].reshape(-1, block), axis=1)

    # z-score x
    fs_ds = 1 / (60* 10)  # 1 sample per 10 min => 1/600 Hz

    # detrend
    #x = np.nan_to_num(x)
    #x = sig.detrend(x)

    N = len(x)
    fft_vals = rfft(x)
    freqs = rfftfreq(N, d=1/fs_ds)
    power = np.abs(fft_vals)**2

    # drop DC
    freqs = freqs[1:]
    power = power[1:]

    period_hours = 1 / freqs / 3600

    # choose a meaningful range (example: 1h to 72h)
    mask = (period_hours >= 1) & (period_hours <= 72)

    eps = 1e-12
    plt.figure(figsize=(8,6))
    plt.subplot(1, 2, 1)
    plt.plot(period_hours, np.log(power + eps))
    plt.gca().invert_xaxis()
    # log x scale
    plt.xscale('log')
    plt.xlabel("Period (hours)")
    plt.ylabel("Log Power")
    # plt vertical line at 24h
    plt.axvline(x=24, color='r', linestyle='--', label='24h')
    plt.axvline(x=12, color='g', linestyle='--', label='12h')
    plt.legend()
    plt.subplot(1, 2, 2)
    # plot here jsut the time domain
    plt.plot(x)
    plt.title("10-min averaged signal")
    plt.xlabel("10-min blocks")
    plt.ylabel("Z-scored amplitude")
    plt.tight_layout()
    plt.savefig(f"figures/eda/{file_[:].replace('.npy', '')}.png")
    plt.show()

# shuffle files

random.shuffle(files)

for file in files:
    if file.endswith(".npy"):
        plot_file(file)

# nohup python stft_analysis_multiday.py > stft_analysis_multiday.log 2>&1 &

# plt.figure()
# plt.plot(x)
# plt.title("10-min averaged signal")
# plt.xlabel("10-min blocks")
# plt.ylabel("Z-scored amplitude")
# plt.savefig("10min_averaged_signal.png")

# # just run an fft on this signal?


# signal = dat[:250*60*10]   # first 60 seconds like your example

# # Define frequencies of interest
# # logarithmically spaced frequencies from 0.01 to 120 Hz
# freqs = np.logspace(np.log10(0.01), np.log10(120), num=100)
# freqs = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 12, 15, 20, 25, 30, 40, 50,
#          60, 70, 80, 90, 100]

# # Convert frequencies to scales
# wavelet = 'cmor1.5-1.0'  # complex Morlet
# scales = pywt.central_frequency(wavelet) * fs / freqs

# # Continuous Wavelet Transform
# coeffs, frequencies = pywt.cwt(signal, scales, wavelet, sampling_period=1/fs)

# # Power
# power = np.abs(coeffs)

# # Time vector
# t = np.arange(signal.shape[0]) / fs

# plt.figure(figsize=(12, 6))

# plt.pcolormesh(t, np.arange(frequencies.shape[0]), np.log(power),
#                shading='auto')

# plt.yticks(frequencies[::5],
#           labels=np.round(frequencies[::5], 2))

# plt.title('Wavelet (CWT) Magnitude')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.colorbar(label='Log Power')

# plt.tight_layout()
# plt.savefig("wavelet_magnitude.png")

# ########################

# dat_l = dat[:120*250]

# x = np.nan_to_num(dat_l[np.newaxis, np.newaxis, :])  # shape (epochs, channels, time)

# freqs = np.arange(2, 100, 1)

# power = mne.time_frequency.tfr_array_multitaper(
#     x,
#     sfreq=250,
#     freqs=freqs,
#     n_cycles=freqs / 2,
#     output='power'
# )
# n_times = x.shape[-1]
# t = np.arange(n_times) / 250


# plt.figure(figsize=(12, 6))
# plt.pcolormesh(t, freqs, np.log(power[0, 0]), shading='auto')
# plt.title('Multitaper Power Spectral Density')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.colorbar(label='Log Power')
# plt.savefig("multitaper_power_spectral_density.png")    

# dat_l = dat[:3600*250]

# f, t, Zxx = scipy.signal.stft(dat_l, fs=250, nperseg=250, noverlap=125)


