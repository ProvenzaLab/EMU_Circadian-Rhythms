import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
from scipy.stats import ttest_ind

df = pd.read_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\circ_power_added_regions.csv")

i = df["power_24hr"].idxmax()
row = df.loc[i]

print("Highest power_24hr row:")
print("Region:", row["ROI_D2009_3mm"])
print("Band:", row["band"])

df_noShuffle = df[df["shuffled"] == False]

bands = ['delta', 'theta', 'alpha', 'beta', 'low_gamma', 'high_gamma']


top5_list = []
for band in bands:
    df_band = df_noShuffle[df_noShuffle["band"] == band]

    region_means = (
        df_band.groupby("ROI_D2009_3mm", as_index=False)["power_24hr"]
        .mean()
        .rename(columns={"power_24hr": "mean_power_24hr"})
        .sort_values("mean_power_24hr", ascending=False)
        .head(5)
    )
    region_means["band"] = band
    top5_list.append(region_means)

top5 = pd.concat(top5_list, ignore_index=True)
top_reg = top5[["ROI_D2009_3mm"]].copy()

bottom5_list = []
for band in bands:
    df_band = df_noShuffle[df_noShuffle["band"] == band]

    region_means = (
        df_band.groupby("ROI_D2009_3mm", as_index=False)["power_24hr"]
        .mean()
        .rename(columns={"power_24hr": "mean_power_24hr"})
        .sort_values("mean_power_24hr", ascending=True)
        .head(5)
    )
    region_means["band"] = band
    bottom5_list.append(region_means)

bottom5 = pd.concat(bottom5_list, ignore_index=True)
bottom_reg = bottom5[["ROI_D2009_3mm"]].copy() #all bottom regions across the 6 bands




for band in bands:
    # top 5 regions for this band, ordered high → low
    top_regions = (
        top5.loc[top5["band"] == band]
        .sort_values("mean_power_24hr", ascending=False)["ROI_D2009_3mm"]
        .tolist()
    )
    df_plot = df_noShuffle[
        (df_noShuffle["band"] == band) &
        (df_noShuffle["ROI_D2009_3mm"].isin(top_regions))
    ]

    data = [
        df_plot.loc[df_plot["ROI_D2009_3mm"] == region, "power_24hr"].values
        for region in top_regions
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot(data, showfliers=False)

    ax.set_xticks(range(1, len(top_regions) + 1))
    ax.set_xticklabels(top_regions, rotation=45, ha="right")

    ax.set_title(f"Top 5 Regions by Mean 24h Power – {band}")
    ax.set_ylabel("24h Power")

    plt.tight_layout()
    plt.savefig(fr"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\Boxplots_topbottom5\TOP_box_{band}.png", dpi=300)
    plt.close()


for band in bands:
    # top 5 regions for this band, ordered high → low
    bottom_regions = (
        bottom5.loc[bottom5["band"] == band]
        .sort_values("mean_power_24hr", ascending=True)["ROI_D2009_3mm"]
        .tolist()
    )
    df_plot = df_noShuffle[
        (df_noShuffle["band"] == band) &
        (df_noShuffle["ROI_D2009_3mm"].isin(bottom_regions))
    ]

    data = [
        df_plot.loc[df_plot["ROI_D2009_3mm"] == region, "power_24hr"].values
        for region in bottom_regions
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot(data, showfliers=False)

    ax.set_xticks(range(1, len(bottom_regions) + 1))
    ax.set_xticklabels(bottom_regions, rotation=45, ha="right")

    ax.set_title(f"Bottom 5 Regions by Mean 24h Power – {band}")
    ax.set_ylabel("24h Power")

    plt.tight_layout()
    plt.savefig(fr"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\Boxplots_topbottom5\BOTTOM_box_{band}.png", dpi=300)
    plt.close()



def plot_side_by_side(df, regions_df, band, tag, out_path):
    # regions_df is top5 or bottom5; must have columns ["band","ROI_D2009_3mm"]
    regions = regions_df.loc[regions_df["band"] == band, "ROI_D2009_3mm"].tolist()

    # Pull data for those regions only
    df_band = df[(df["band"] == band) & (df["ROI_D2009_3mm"].isin(regions))].copy()

    positions = []
    data = []
    colors = []  # 0 = not shuffled, 1 = shuffled (we'll color after boxplot)

    gap = 1.0          # gap between regions
    offset = 0.18      # separation within region
    box_w = 0.30

    for r, region in enumerate(regions):
        base = r * gap

        vals_ns = df_band[(df_band["ROI_D2009_3mm"] == region) & (df_band["shuffled"] == False)]["power_24hr"].dropna().values
        vals_sh = df_band[(df_band["ROI_D2009_3mm"] == region) & (df_band["shuffled"] == True)]["power_24hr"].dropna().values

        # even if one side is missing, keep alignment by adding empty arrays (boxplot will skip if empty)
        if len(vals_ns) > 0:
            data.append(vals_ns); positions.append(base - offset); colors.append(0)
        if len(vals_sh) > 0:
            data.append(vals_sh); positions.append(base + offset); colors.append(1)

    fig, ax = plt.subplots(figsize=(10, 6))

    bp = ax.boxplot(
        data,
        positions=positions,
        widths=box_w,
        patch_artist=True,
        showfliers=False
    )

    # Color boxes: default matplotlib colors, but two consistent fills
    for box, c in zip(bp["boxes"], colors):
        if c == 0:
            box.set_facecolor("white")   # not shuffled
        else:
            box.set_facecolor("lightgray")  # shuffled

    # Region tick labels at center of each pair
    ax.set_xticks([r * gap for r in range(len(regions))])
    ax.set_xticklabels(regions, rotation=45, ha="right", fontsize=8)

    ax.set_title(f"{tag} 5 Regions – {band}: Not-shuffled vs Shuffled")
    ax.set_ylabel("24h Power")

    # simple legend
    import matplotlib.patches as mpatches
    ax.legend(
        handles=[
            mpatches.Patch(facecolor="white", edgecolor="black", label="Not shuffled"),
            mpatches.Patch(facecolor="lightgray", edgecolor="black", label="Shuffled"),
        ],
        loc="upper right"
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


for band in bands:
    plot_side_by_side(
        df=df,
        regions_df=top5,
        band=band,
        tag="Top",
        out_path=fr"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\Boxplots_sidebyside\TOP_box_{band}_side_by_side.png"
    )

    plot_side_by_side(
        df=df,
        regions_df=bottom5,
        band=band,
        tag="Bottom",
        out_path=fr"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\Boxplots_sidebyside\BOTTOM_box_{band}_side_by_side.png"
    )
    

def run_shuffled_ttests(df, regions_df, bands, label):
    """
    df: full dataframe (contains shuffled True/False)
    regions_df: top5 or bottom5 dataframe
    label: 'top' or 'bottom'
    """
    results = []

    for band in bands:
        regions = regions_df.loc[regions_df["band"] == band, "ROI_D2009_3mm"]
        
        for region in regions:
            df_reg = df[
                (df["band"] == band) &
                (df["ROI_D2009_3mm"] == region)
            ]

            vals_ns = df_reg[df_reg["shuffled"] == False]["power_24hr"].dropna().values
            vals_sh = df_reg[df_reg["shuffled"] == True]["power_24hr"].dropna().values

            # skip if not enough data
            if len(vals_ns) < 10 or len(vals_sh) < 10:
                continue

            tstat, pval = ttest_ind(vals_ns, vals_sh, equal_var=False,alternative="greater")

            results.append({
                "band": band,
                "region": region,
                "group": label,
                "n_not_shuffled": len(vals_ns),
                "n_shuffled": len(vals_sh),
                "mean_not_shuffled": vals_ns.mean(),
                "mean_shuffled": vals_sh.mean(),
                "t_stat": tstat,
                "p_value": pval
            })

    return pd.DataFrame(results)

ttest_top = run_shuffled_ttests(df, top5, bands, label="top")
ttest_top.to_csv(rf"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\TOP_ttest_{band}_side_by_side.csv",index=False)

ttest_bottom = run_shuffled_ttests(df, bottom5, bands, label="bottom")
ttest_bottom.to_csv(rf"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\BOTTOM_ttest_{band}_side_by_side.csv",index=False)