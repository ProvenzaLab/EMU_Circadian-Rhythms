import os
import datetime
import argparse
import csv

from neo.io import BlackrockIO
from neo.rawio import BlackrockRawIO


# Keep paths aligned with parse_data_into_npy_spikes.py
PATH_DATA = "/mnt/datalake/data/emu"
PATH_OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/data_250Hz_spikes"
DEFAULT_OUTPUT_CSV = "available_spike_progress.csv"
DEFAULT_SUBJECTS = [
    "YFADatafile",
    "YFBDatafile",
    "YFCDatafile",
    "YFDDatafile",
    "YFEDatafile",
    "YFFDatafile",
    "YFGDatafile",
    "YFHDatafile",
    "YFIDatafile",
    "YFJDatafile",
    "YFKDatafile",
    "YFLDatafile",
    "YFMDatafile",
    "YFNDatafile",
    "YFODatafile",
    "YFPDatafile",
    "YFQDatafile",
    "YFRDatafile",
    "YFSDatafile",
    "YFTDatafile",
    "YFUDatafile",
    "YFVDatafile",
]


def get_recording_datetime_utc(ns5_file_path: str):
    """
    Return recording datetime in UTC using a lightweight header read first,
    then fallback to lazy block read if needed.
    """
    try:
        r = BlackrockRawIO(filename=ns5_file_path)
        r.parse_header()

        io = BlackrockIO(filename=ns5_file_path)
        blk = io.read_block(lazy=True)
        dt = blk.segments[0].rec_datetime
        return dt.astimezone(datetime.timezone.utc)
    except Exception:
        return None


def write_progress_csv(output_csv: str, subject_filter=None):
    subjects = sorted([s for s in os.listdir(PATH_DATA) if s.startswith("YF")])

    if subject_filter is not None:
        subjects = [s for s in subjects if s in subject_filter]

    fieldnames = ["data_range_path", "l_ns5_file", "sub_path_out", "subject", "exists"]
    total = 0
    n_exists = 0

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for subject in subjects:
            subject_path = os.path.join(PATH_DATA, subject)
            subject_path_data = os.path.join(subject_path, "DATA")
            sub_path_out = os.path.join(PATH_OUT, subject)

            if not os.path.isdir(subject_path_data):
                continue

            data_ranges = sorted([f for f in os.listdir(subject_path_data) if f.startswith("2")])
            for data_range in data_ranges:
                data_range_path = os.path.join(subject_path_data, data_range)
                if not os.path.isdir(data_range_path):
                    continue

                # Match the parser's selection logic (NSP2*.ns5)
                l_ns5 = sorted(
                    [f for f in os.listdir(data_range_path) if f.endswith("ns5") and f.startswith("NSP2")]
                )

                for l_ns5_file in l_ns5:
                    ns5_file_path = os.path.join(data_range_path, l_ns5_file)
                    dt = get_recording_datetime_utc(ns5_file_path)

                    if dt is None:
                        status = "not exist"
                    else:
                        str_dt = dt.strftime("%Y%m%dT%H%M%S")
                        out_data_path = os.path.join(sub_path_out, f"{subject}_{str_dt}_sbp_mua.npy")
                        out_channels_path = os.path.join(sub_path_out, f"{subject}_{str_dt}_channels.csv")

                        if os.path.exists(out_data_path) and os.path.exists(out_channels_path):
                            status = "exists"
                        else:
                            status = "not exist"

                    row = {
                        "data_range_path": data_range_path,
                        "l_ns5_file": l_ns5_file,
                        "sub_path_out": sub_path_out,
                        "subject": subject,
                        "exists": status,
                    }
                    writer.writerow(row)
                    csvfile.flush()

                    total += 1
                    if status == "exists":
                        n_exists += 1

                    print(f"{subject} | {data_range} | {l_ns5_file} | {status}")

    return total, n_exists


def main():
    parser = argparse.ArgumentParser(description="Check availability of spike output files.")
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_CSV,
        help="Path to output CSV file.",
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        default=None,
        help="Optional subject IDs to include (e.g., YFA YFB). Defaults to YFA..YFV list used in spike pipeline.",
    )
    args = parser.parse_args()

    subject_filter = args.subjects if args.subjects is not None else DEFAULT_SUBJECTS

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    total, n_exists = write_progress_csv(args.output, subject_filter=subject_filter)
    n_missing = total - n_exists
    print(f"Wrote {args.output}")
    print(f"Total rows: {total} | exists: {n_exists} | not exist: {n_missing}")


if __name__ == "__main__":
    main()

#nohup python available_spike_progress.py --output available_spike_progress.csv > progress_check.out 2>&1 &
