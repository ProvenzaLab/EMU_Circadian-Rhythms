import os
import sys
import pandas as pd
from parse_data_into_npy_TRD import process_file, ns3_header

if __name__ == "__main__":
    
    files_run = pd.read_csv("ns5_files_to_process_TRD014.csv")

    idx_run = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if idx_run >= len(files_run):
        print(f"Index {idx_run} out of range for files_run with length {len(files_run)}")
        sys.exit(1)
    
    row = files_run.iloc[idx_run]
    data_range_path = row["data_range_path"]
    ns5_file = row["ns5_file"]
    sub_path_out = row["sub_path_out"]
    subject = row["subject"]

    print(f"Processing file {ns5_file} for subject {subject} at index {idx_run}")
    process_file(data_range_path, ns5_file, sub_path_out, subject)