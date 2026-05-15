

import numpy as np
data = np.load("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/continuous_data/YFR_RT2cHb09_20250701-055423.000.npy")
fs = 250

def run_lengths(mask):
    padded = np.concatenate(([False], mask, [False]))
    changes = np.diff(padded.astype(np.int8))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    lengths = ends - starts
    return starts, ends, lengths

zero_mask = (data == 0)
nan_mask = np.isnan(data)

z_starts, z_ends, z_lengths = run_lengths(zero_mask)
n_starts, n_ends, n_lengths = run_lengths(nan_mask)

print("ZERO RUNS")
print("num runs:", len(z_lengths))
if len(z_lengths) > 0:
    i = np.argmax(z_lengths)
    print("longest run:",
          z_lengths[i], "samples",
          f"({z_lengths[i]/fs:.2f} sec)",
          "start =", z_starts[i],
          "end =", z_ends[i]-1)
else:
    print("none")

print("\nNAN RUNS")
print("num runs:", len(n_lengths))
if len(n_lengths) > 0:
    i = np.argmax(n_lengths)
    print("longest run:",
          n_lengths[i], "samples",
          f"({n_lengths[i]/fs:.2f} sec)",
          "start =", n_starts[i],
          "end =", n_ends[i]-1)
else:
    print("none")