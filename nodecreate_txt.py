import os
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

    # print to console
    #print(text)

    # save to file
    with open(out_file, "w") as f:
        f.write(text)



folder = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/CSVs/electrodes_new_mni152" 

for file in os.listdir(folder):
    if not file.endswith(".csv"):
        continue

    path = os.path.join(folder, file)
    df = pd.read_csv(path)

    if {"MNI152_x", "MNI152_y", "MNI152_z"}.issubset(df.columns):
        x = df["MNI152_x"]
        y = df["MNI152_y"]
        z = df["MNI152_z"]
    else:
        print(f"Skipping {file} (missing MNI152 columns)")
        continue

    n = len(df)

    # simple defaults (edit later if needed)
    var_colorcode = [1] * n
    radius = [2] * n

    out_file = os.path.join(
        "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/CSVs/electrodes_new_mni152/txt_files",
        file.replace(".csv", "_nodecreate.txt")
    )

    write_nodecreate_txt(x, y, z, var_colorcode, radius, out_file)



