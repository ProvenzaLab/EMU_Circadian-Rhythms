import os
import numpy as np
from datetime import datetime, timedelta
from joblib import Parallel, delayed
import matplotlib.pyplot as plt

ROOT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/chunks_out_fixed_new"     
OUT = "/mnt/labworlds/Provenza/EMU_Circadian-Rhythms/testFolder"
FS = 250

def parse_filename(filename):
   
    base = filename.replace(".npy", "")
    parts = base.split("_")

    dt_str = parts[2]
    start_dt = datetime.strptime(dt_str, "%Y%m%d-%H%M%S")

    return start_dt

def make_nan_gap(n_missing):
    
   return np.full(n_missing, np.nan, dtype=np.float64)
    

def get_time(item):
    return item[1]

def process_electrode(patient, electrode):
    folder = os.path.join(ROOT, patient, electrode)

    try:
        files = [f for f in os.listdir(folder) if f.endswith(".npy")]
        
        parsed = []
        for f in files:
            try:
                start_dt = parse_filename(f)
                parsed.append((f, start_dt))
            except Exception as e:
                return f"Failed {patient}/{electrode}: bad filename {f} ({e})"

        parsed.sort(key=get_time)

        combined_parts = []
        prev_end_dt = None
  

        for i, (fname, start_dt) in enumerate(parsed):
            path = os.path.join(folder, fname)
            data = np.load(path).astype(np.float64) 

            
            if prev_end_dt is not None: #check that its not first file in contact/patient
                gap_seconds = (start_dt - prev_end_dt).total_seconds()

                # gap_seconds > 0 means missing data
                if gap_seconds > 0:
                    n_missing = int(round(gap_seconds * FS)) #samples missing
                    if n_missing > 0:
                        gap_array = make_nan_gap(n_missing)
                        combined_parts.append(gap_array)

                # gap_seconds < 0 means overlap
                elif gap_seconds < 0:
                    n_overlap = int(round(abs(gap_seconds) * FS))

                    # If the entire new file is overlapped, skip it
                    if n_overlap >= len(data):
                        continue

                    # Trim the overlapping portion from the start of the new file
                    data = data[n_overlap:]

            combined_parts.append(data)

            duration_seconds = len(data) / FS
            prev_end_dt = start_dt + timedelta(seconds=duration_seconds)

        combined = np.concatenate(combined_parts, axis=0) #need to concatenate after all the appends
        plt.figure(figsize=(12, 4))
        plt.plot(combined)
        
        plt.xlabel("Samples")
        plt.ylabel("Voltage")

        plot_path = os.path.join(OUT, f"{patient}_{electrode}_combined_plot.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()
        

        out_path = os.path.join(OUT, f"{patient}_{electrode}_{parsed[0][1].strftime('%Y%m%d-%H%M%S.%f')}.npy")

        np.save(out_path, combined)

    except Exception as e:
        return f"Failed {patient}/{electrode}: {e}"


if __name__ == "__main__":
    jobs = []
    for patient in os.listdir(ROOT):
        patient_path = os.path.join(ROOT, patient)

        for electrode in os.listdir(patient_path):
            electrode_path = os.path.join(patient_path, electrode)

            jobs.append((patient, electrode))


    Parallel(n_jobs=25)(
        delayed(process_electrode)(patient, electrode)
        for patient, electrode in jobs
    )

# jobs = sorted(jobs)
# print("Number of jobs:", len(jobs))
# print("Jobs being run:", jobs[:10])

# for patient, electrode in jobs[:10]:
#     print(f"Running {patient}/{electrode}")
#     result = process_electrode(patient, electrode)
#     print(result)
