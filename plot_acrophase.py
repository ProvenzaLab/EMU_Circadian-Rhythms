import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

df = pd.read_csv("acrophase/cosinor_results.csv")

plt.figure(figsize=(7, 4))
sns.displot(
    data=df,
    x="left_cosinor_acrophase",
    hue="band",
    hue_order=["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"],
    palette="viridis",
    kind="kde",)
plt.xlim(1, 23)
plt.savefig("acrophase/all_dist.pdf")