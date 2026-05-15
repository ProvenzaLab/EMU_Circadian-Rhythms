import os
import numpy as np
import pandas as pd

def write_nodecreate_txt(
    mni152_x, mni152_y, mni152_z,
    var_colorcode, radius,
    out_file="nodecreate.txt",
    precision=2
):
    """
    Generate NODECREATE block from MNI152 coordinates,
    a color-coding variable, and radius arrays.
    """

    n = len(mni152_x)
    if not (
        len(mni152_y) == len(mni152_z) ==
        len(var_colorcode) == len(radius) == n
    ):
        raise ValueError(
            "mni152_x, mni152_y, mni152_z, var_colorcode, and radius must have the same length"
        )

    fmt = f"{{:.{precision}f}}"

    x_str = ", ".join(fmt.format(v) for v in mni152_x)
    y_str = ", ".join(fmt.format(v) for v in mni152_y)
    z_str = ", ".join(fmt.format(v) for v in mni152_z)
    var_str = ", ".join(fmt.format(v) for v in var_colorcode)
    radius_str = ", ".join(fmt.format(v) for v in radius)

    text = f"""BEGIN
NODECREATE('',
[{x_str}],
[{y_str}],
[{z_str}],
[{var_str}],
[{radius_str}]
);
END.
"""

    # save to file
    with open(out_file, "w") as f:
        f.write(text)



folder = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/CSVs/electrodes_manuscript" 
var_folder = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"

features = ["circadian_power_24hr","exponent_power_24hr","offset_power_24hr"]
f_names = ["delta", "theta", "alpha", "beta", "low_gamma", "high_gamma"]

globalMaxPower = -np.inf
globalMinPower = np.inf

globalMaxOff = -np.inf
globalMinOff = np.inf

globalMaxExp = -np.inf
globalMinExp = np.inf

for root, dirs, files in os.walk(var_folder):
   
    for file in files:
        df=pd.read_csv(os.path.join(root,file))
        maxPower = df["circadian_power_24hr"].max()
        minPower = df["circadian_power_24hr"].min()

        maxOff = df["offset_power_24hr"].max()
        minOff = df["offset_power_24hr"].min()

        maxExp = df["exponent_power_24hr"].max()
        minExp = df["exponent_power_24hr"].min()
        
        globalMaxPower = max(globalMaxPower, maxPower)
        globalMinPower = min(globalMinPower, minPower)

        globalMaxOff = max(globalMaxOff, maxOff)
        globalMinOff = min(globalMinOff, minOff)

        globalMaxExp = max(globalMaxExp, maxExp)
        globalMinExp = min(globalMinExp, minExp)


for feature in features:
    for f_band in f_names:

        all_x, all_y, all_z = [], [], []
        all_vals = []


     
        for file in os.listdir(folder):
       

        
            if not file.endswith(".csv"):
                continue

            path = os.path.join(folder, file)
            df = pd.read_csv(path)
            base = file.replace(".csv", "")
            parts = base.split("_")

            patient = parts[0]
            patient = patient.replace("-electrodes","")
            
            pat_path = os.path.join(var_folder,patient)
            

            power_path = os.path.join(pat_path, f"{patient}_ALL_ELECTRODES.csv")
            df_power = pd.read_csv(power_path)
            df_power = df_power[df_power["frequency_band"] == f_band].copy() #get one frequency band

            df["Label"] = df["Label"].astype(str).str.strip()

            df_power["Label"] = (
                df_power["Label"]
                .astype(str)
                .str.strip()
                .str.split("-")
                .str[0]
                )

            df_power_sub = df_power[[
                "Label",
                f"{feature}"
            ]].copy()

            df_merged = df.merge(df_power_sub, on="Label", how="left")
            df_merged = df_merged.dropna(subset=[feature])

            all_x.extend(df_merged["MNI152_x"].tolist())
            all_y.extend(df_merged["MNI152_y"].tolist())
            all_z.extend(df_merged["MNI152_z"].tolist())
            vals = pd.to_numeric(df_merged[feature], errors="coerce")

           
            all_vals.extend(vals.tolist())

            if feature == "circadian_power_24hr":
                fmin = globalMinPower
                fmax = globalMaxPower
            elif feature == "offset_power_24hr":
                fmin = globalMinOff
                fmax = globalMaxOff
            elif feature == "exponent_power_24hr":
                fmin = globalMinExp
                fmax = globalMaxExp

        vals = pd.Series(all_vals)
        denom = fmax - fmin  #min-max scaling means that no matter what my range is, it gets stretched to entire color scale [0,1]
        if denom == 0:
            var_colorcode = np.zeros(len(vals), dtype=float)
        else:
            var_colorcode = ((vals - fmin) / denom).to_numpy(dtype=float)
        
        var_colorcode = [
             0.01 if round(v, 2) == 0 else round(v, 2)
             for v in var_colorcode
        ]   
    
        radius = [2] * len(all_x)
        

        txtsave = os.path.join("/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/Manuscript_Plots/BrainPlots",f"{feature}_{f_band}_brainTESTONLY.txt")
        
        if len(all_x) == 0:
            continue

        write_nodecreate_txt(all_x, all_y, all_z, var_colorcode, radius, txtsave)