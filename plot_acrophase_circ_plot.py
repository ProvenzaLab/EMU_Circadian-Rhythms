import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("acrophase/cosinor_results.csv")

# ----- binning: EXACT half-hour bins -----
#bin_hours = np.arange(0, 24.5, 0.5)          # 0, 0.5, ..., 24

theta_bins = np.linspace(0, 2*np.pi, 49)
bin_hours = np.linspace(0, 24, 49)

theta_centers = (theta_bins[:-1] + theta_bins[1:]) / 2 - (np.pi / 48)  # center adjustment

# ----- bands in desired order -----
bands = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

# ----- colormap -----
cmap = plt.cm.viridis
colors = cmap(np.linspace(0.1, 0.9, len(bands)))

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection="polar")

for band, color in zip(bands, colors):
    if band not in df["band"].unique():
        continue

    df_band = df[df["band"] == band]

    # hours → radians
    theta = df_band["left_cosinor_acrophase"].values / 24 * 2 * np.pi

    # histogram
    counts, _ = np.histogram(theta, bins=theta_bins)

    # close the circle
    theta_plot = np.append(theta_centers, theta_centers[0])
    counts_plot = np.append(counts, counts[0])

    # continuous circular line
    ax.plot(
        theta_plot,
        counts_plot,
        linewidth=2,
        color=color,
        label=band
    )

# ----- circadian aesthetics -----
ax.set_theta_zero_location("N")   # 0 h at top
ax.set_theta_direction(-1)        # clockwise

ax.set_thetagrids(
    np.arange(0, 360, 45),
    labels=[f"{h} h" for h in range(0, 24, 3)]
)

ax.set_title("Circadian Distribution of Acrophase", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

plt.savefig("acrophase/circadian_lines_viridis_30min.pdf",
            dpi=300, bbox_inches="tight")
plt.show()