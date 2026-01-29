import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

df = pd.read_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\circ_power_added_regions.csv")

df_noShuffle = df[df["shuffled"] == False]

bands = ['delta', 'theta', 'alpha', 'beta', 'low_gamma', 'high_gamma']

RPF = 10
for band in bands:
    df_band = df_noShuffle[df_noShuffle["band"] == band]

    regions_all = sorted(df_band["ROI_D2009_3mm"].dropna().unique())
    patients = sorted(df_band["patient"].unique())

    region_gap = len(patients) + 2   # how wide each region block is
    box_w = 0.8                      # width of each patient box
    

    colors = plt.cm.tab20(np.linspace(0, 1, len(patients)))  # auto colors
    patient_to_color = dict(zip(patients, colors))


    positions = []
    box_data = []
    box_patient = []

   

    for page_start in range(0, len(regions_all), RPF):
        regions = regions_all[page_start:page_start + RPF]
        page_num = page_start // RPF + 1

        fig, ax = plt.subplots(figsize=(max(12, 0.6 * len(regions)), 6))


        positions = []
        box_patient = []
        box_data = []
        for r,region in enumerate(regions):
            df_region = df_band[df_band["ROI_D2009_3mm"] == region]
            base = r * region_gap
            for i, patient in enumerate(patients):
                vals = df_region.loc[df_region["patient"] == patient,"power_24hr"].dropna().values

                if len(vals) == 0:
                    continue

                box_data.append(vals)
                positions.append(base + i)
                box_patient.append(patient)
         
          

        
        bp=ax.boxplot(
            box_data,
            positions=positions,
            widths=box_w,
            patch_artist=True,
            showfliers=False
        )

        for box, pat in zip(bp["boxes"], box_patient):
            box.set_facecolor(patient_to_color[pat])

        region_centers = [r * region_gap + (len(patients) - 1) / 2 for r in range(len(regions))]
        ax.set_xticks(region_centers)
        ax.set_xticklabels(regions, rotation=45, ha="right", fontsize=8)

        ax.set_title(f"24h Power by Region – {band}")
        ax.set_ylabel("24h Power")
        handles = [mpatches.Patch(color=patient_to_color[p], label=p) for p in patients]
        ax.legend(handles=handles, title="Patient", bbox_to_anchor=(1.02, 1), loc="upper left")

        plt.tight_layout()
        plt.savefig(fr"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\Boxplots\power_24h_boxplot_{band}-page{page_start//RPF + 1}.png", dpi=300)
        plt.close()