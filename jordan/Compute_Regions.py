import numpy as np
import pandas as pd
import os


df_regions = pd.read_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\CSVs\all_patients.csv")
df_regions = df_regions.rename(columns={
    "Label": "channel",
})

df_power = pd.read_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\circadian_power_24hr_summary.csv")
df_power["patient"] = df_power["patient"].str.replace("Datafile", "", regex=False)
df_power["channel"] = df_power["channel"].str.replace(r"-\d+$", "", regex=True)

df_power_new = df_power.merge(df_regions, on=["patient","channel"], how="left")

df_power_new.to_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\added_regions\circ_power_added_regions.csv", index=False)





