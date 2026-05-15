 - parse_data_into_npy.py -> write data_250Hz_new (has to be re-run for TRD)
 - 1_concat_patient_data.py -> chunks_out_fixed_new
 - continuous_making.py -> continuous_data_new
 - continuous_file_processing.py -> chunks_power_continuous_new 
 - get_circadian_power.py -> all_electrodes_24Power_new

    naming convention:
    {patient}_{channel}_(start_time).npy
    save in continuous_data_new
    (delete everything in folder)

    