import os
import sys

import pandas as pd

from parse_data_into_npy_spikes import process_file


DEFAULT_CSV_PATH = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/available_spike_progress.csv"
REQUIRED_COLUMNS = ["data_range_path", "l_ns5_file", "sub_path_out", "subject", "exists"]


def load_rows(csv_path: str) -> pd.DataFrame:
	df = pd.read_csv(csv_path)
	missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
	if missing_columns:
		raise ValueError(f"Missing required columns in {csv_path}: {missing_columns}")
	return df


def exists_is_true(exists_value) -> bool:
	if pd.isna(exists_value):
		return False
	value = str(exists_value).strip().lower()
	return value in {"true", "1", "yes", "y", "exists"}


def process_csv_row(row: pd.Series, row_index: int, total_rows: int):
	data_range_path = row["data_range_path"]
	ns5_file = row["l_ns5_file"]
	sub_path_out = row["sub_path_out"]
	subject = row["subject"]
	exists_value = row["exists"]

	if exists_is_true(exists_value):
		print(
			f"Skipping row {row_index + 1}/{total_rows}: "
			f"subject={subject}, ns5_file={ns5_file}, exists={exists_value}"
		)
		return

	os.makedirs(sub_path_out, exist_ok=True)

	print(
		f"Processing row {row_index + 1}/{total_rows}: "
		f"subject={subject}, ns5_file={ns5_file}"
	)
	process_file(data_range_path, ns5_file, sub_path_out, subject)


def main():
	df = load_rows(DEFAULT_CSV_PATH)
	total_rows = len(df)
	if total_rows == 0:
		print(f"No rows found in {DEFAULT_CSV_PATH}")
		return

	row_index = int(sys.argv[1]) if len(sys.argv) > 1 else 5944
	if row_index < 0 or row_index >= total_rows:
		raise IndexError(f"Row index out of range: {row_index}. CSV has {total_rows} rows.")

	process_csv_row(df.iloc[row_index], row_index, total_rows)


if __name__ == "__main__":
	main()
