import pandas as pd
import numpy as np
from scipy.stats import ttest_ind




df =pd.read_csv(r"Z:\Provenza\EMU_Circadian-Rhythms\circ_power\circadian_power_24hr_summary.csv")


real = df.loc[df["shuffled"] == False, "power_24hr"].dropna()
shuf = df.loc[df["shuffled"] == True, "power_24hr"].dropna()

tstat, pval = ttest_ind(real, shuf, equal_var=False)

print(f"Welch t-test: t = {tstat:.3f}, p = {pval:.30e}")
print(pval)