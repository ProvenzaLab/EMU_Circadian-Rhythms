import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
import seaborn as sns

sns.set_theme(style="whitegrid")

df = pd.read_csv("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/cosinor_results.csv")
bands = ['delta','theta','alpha','beta','low_gamma','high_gamma']


df["acrophase_hr"] = (
    df["left_cosinor_acrophase"]
    .dropna()
    .mul(6)
    .round()
    .div(6)
    % 24
)

step = 10 / 60  # 1/6 hr
bins = np.arange(0, 24 + step, step)
plt.figure(figsize=(10, 6))
sns.histplot(
    data=df,
    x="acrophase_hr",
    hue="band",
    bins=bins,
    element="step",   
    stat="count",
    common_bins=True,
    common_norm=False
)

plt.xlabel("Acrophase (hours)")
plt.ylabel("Count")
plt.title("Cosinor Acrophase Distribution — All Bands")
plt.xlim(0, 24)
plt.tight_layout()
plt.savefig(
    r"Z:\Provenza\EMU_Circadian-Rhythms\acrophase\All_Bands\acrophase_allbands_overlay_hist.png",
    dpi=300
)
plt.close()

# Alpha band only

# for band in bands:
#     df_band = df[df["band"] == band]

#     acrophase_hours = (
#         df_band["left_cosinor_acrophase"]
#         .dropna()
#         .mul(6)        # convert hours → 10-minute bins
#         .round()       # round to nearest bin
#         .div(6)        # back to hours
#         % 24
#     )


#     step = 10 / 60  # hours = 1/6

#     bins = np.arange(0, 24 + step, step)


#     plt.figure(figsize=(10, 4))
#     plt.hist(acrophase_hours, bins=bins)
#     plt.xlabel("Acrophase (hours)")
#     plt.ylabel("Count")
#     plt.title(f"{band}-band Cosinor Acrophase Distribution — Both Hemispheres")
#     plt.xlim(0, 24)
#     plt.tight_layout()
#     mplcursors.cursor(hover=True)
#     #plt.show()
#     plt.savefig(rf"Z:\Provenza\EMU_Circadian-Rhythms\acrophase\All_Bands\testing_{band}_acrophase_hist.png", dpi=300)
#     plt.close()





# counts_left, bin_edges = np.histogram(acrophase_hours, bins=bins)

# # Put into a clean table
# hist_left = pd.DataFrame({
#     "bin_start_hr": bin_edges[:-1],
#     "bin_end_hr": bin_edges[1:],
#     "count": counts_left
# })

# hist_left.to_csv(
#     r"Z:\Provenza\EMU_Circadian-Rhythms\acrophase\counts.csv",
#     index=False
# )

print("f")
# acrophase_hours = (
#     df_alpha["right_cosinor_acrophase"]
#     .dropna()
#     .round(1)
#     % 24
# )

# plt.figure(figsize=(10, 4))
# plt.hist(acrophase_hours, bins=bins)
# plt.xlabel("Acrophase (hours)")
# plt.ylabel("Count")
# plt.title("Right Hemi Alpha-band Cosinor Acrophase Distribution — Left Hemisphere")
# plt.xlim(0, 24)
# plt.tight_layout()
# plt.savefig(r"Z:\Provenza\EMU_Circadian-Rhythms\acrophase\Right_alpha_acrophase_hist.png", dpi=300)
# plt.close()

# counts_left, bin_edges = np.histogram(acrophase_hours, bins=bins)

# # Put into a clean table
# hist_right = pd.DataFrame({
#     "bin_start_hr": bin_edges[:-1],
#     "bin_end_hr": bin_edges[1:],
#     "count": counts_left
# })