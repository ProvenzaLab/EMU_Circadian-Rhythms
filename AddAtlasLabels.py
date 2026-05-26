import numpy as np
import os
import pandas as pd
from joblib import Parallel, delayed


#logic, iterate through all of the CSVs saved in "chunks_power_continuous_new" and for each patient for all rows add a column that is the ATLAS label, 
# you can derive the ATLAS label, from the corresponding CSV for that patient saved in the "\CSVs\electrodes_new_mni152" folder
folder = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new"
CSV_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/CSVs/electrodes_new_mni152"
new_path = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/all_electrodes_24Power_new_atlas"

skipped = []
def addAtlasLabel(filePath):
    parts = filePath[1].split("_")
    pat = parts[0]

    df_org = pd.read_csv(os.path.join(filePath[0],filePath[1]))
    CSV_1 = [f for f in os.listdir(CSV_path) if f.startswith(pat)]
    if len(CSV_1) != 1:
        print(pat)
        raise ValueError(f"Expected 1 CSV file for {pat}, found {len(CSV_1)}") #check that only one CSV starts with that patient
    
    CSV = os.path.join(CSV_path,CSV_1[0])
    df = pd.read_csv(CSV)

    df_org["ROI_D2009_3mm"] = None

    

    for idx, value in enumerate(df_org["Label"]):
        value = value.rsplit("-", 1)[0] #splits from the right and only takes 1 part off
       
        row = df[df["Label"] == value]
       
        try:
            atlas_label = row["ROI_D2009_3mm"].iloc[0]
        except IndexError:
            skipped.append((pat,value))
            continue

        df_org.loc[idx, "ROI_D2009_3mm"] = atlas_label
            
    
    base, ext = os.path.splitext(filePath[1])


    new_name = os.path.join(pat,f"{base}_atlas{ext}")
    os.makedirs(os.path.join(new_path,pat), exist_ok=True)

    df_org.to_csv(os.path.join(new_path,new_name), index=False) 




if __name__ == "__main__":

    files = []

    for root, dirs, fs in os.walk(folder):
        for file in fs:
            files.append((root,file))

    files = sorted(files)   
 
    Parallel(n_jobs = 1,verbose=0)(delayed(addAtlasLabel)(path_pass) for path_pass in files)

    with open("skipped_labels.txt", "w") as f:
        for patient, label in skipped:
            f.write(f"{patient} - {label}\n")

    print("DONE.")