import pandas as pd
import os
import numpy as np
import nibabel as nib
import numpy as np

# Load MNI brain image
img = nib.load("CSVs/MNI152_T1_1mm_brain.nii")
data = img.get_fdata()
affine = img.affine



def check_coord_in_the_brain(mni_coord):
    # Example MNI coordinate (x, y, z) in mm
    #mni_coord = np.array([12, -18, 56, 1])

    # Convert MNI -> voxel
    voxel_coord = np.linalg.inv(affine) @ mni_coord
    voxel_coord = np.round(voxel_coord[:3]).astype(int)

    # Check bounds
    inside_bounds = all(
        0 <= voxel_coord[i] < data.shape[i] for i in range(3)
    )

    if inside_bounds and data[tuple(voxel_coord)] > 0:
        return True
    else:
        return False

#csv_files_ = [f for f in os.listdir("CSVs/+electrodes+csvs/+electrodes+csvs/") if f.endswith('.csv')]
csv_files_ = [f for f in os.listdir("CSVs/electrodes_new_mni152/") if f.endswith('.csv')]


l_ = []
for l in csv_files_:
    sub = l[l.find("Y"):l.find("Y")+3]
    #df_ = pd.read_csv(f"CSVs/+electrodes+csvs/+electrodes+csvs/{l}")
    df_ = pd.read_csv(f"CSVs/electrodes_new_mni152/{l}")
    df_['Subject'] = sub
    l_.append(df_)

df_c = pd.concat(l_, ignore_index=True)
# apply on ['MNI152_x', 'MNI152_y', 'MNI152_z'] row-wise
df_c['In_MNI_Brain'] = df_c.apply(
    lambda row: check_coord_in_the_brain(
        [row['MNI152_x'], row['MNI152_y'], row['MNI152_z'], 1]
    ), axis=1
)
# drop all rows where In_MNI_Brain is False
df_c = df_c[df_c['In_MNI_Brain'] == True].copy()
df_c.to_csv("CSVs/combined_electrodes_MNI152.csv", index=False)

def mni305_to_mni152(point):
    point = np.array(list(point) + [1])
    trans = np.array([[0.9975, -0.0073, 0.0176, -0.0429],
                      [0.0146, 1.0009, -0.0024, 1.5496],
                      [-0.0130, -0.0093,  0.9971, 1.1840]])
    return trans @ point

# create df_mni305 and drop all columns where MNI305_x is NaN
df_mni305 = df_c[df_c['MNI305_x'].notna()].copy()
df_mni152 = df_c[df_c['MNI152_x'].notna()].copy()

# convert all mni305 coordinates to mni152
mni152_coords = []
for idx, row in df_mni305.iterrows():
    point_mni305 = [row['MNI305_x'], row['MNI305_y'], row['MNI305_z']]
    point_mni152 = mni305_to_mni152(point_mni305)
    mni152_coords.append(point_mni152[:3])
df_mni305[['MNI152_x', 'MNI152_y', 'MNI152_z']] = mni152_coords
# combine df_mni305 and df_mni152
df_c = pd.concat([df_mni305, df_mni152], ignore_index=True)

df_c.to_csv("CSVs/combined_electrodes.csv", index=False)