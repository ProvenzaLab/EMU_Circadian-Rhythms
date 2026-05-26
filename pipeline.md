 - parse_data_into_npy.py -> data_250Hz_new (has to be re-run for TRD)
 - 1_concat_patient_data.py -> chunks_out_fixed_new
 - continuous_making.py -> continuous_data_new
 - continuous_file_processing.py -> chunks_power_continuous_new 
 - get_circadian_power.py -> all_electrodes_24Power_new


Pipeline written out:
- take ns3 and ns5 and resample to 250 Hz and save out data is .npy and channels as .csv for each file - channels are saved as a file named pat_dt and contain channel names
- for each .npy file that is named with its patient and timestamp, use pat and dt to match it with its channel csv and for each channel save out 10 minute chunks (not necessarily all full) of data as .npy (with timestamp in name)
- for each patient and each contact, make a continuous file, filling in gaps with NaNs
- For each channel and each patient: Then in 10 minute chunks we interpolate if less than 50 NaNs, notch filter (60 Hz), pwelch (no overlap - maximize spatial resolution), use FOOOF to subtract out aperiodic at [3,125], and save out average voltage of data, average band power, aperiodic offset/exponent, save those parameters out for each channel of each patient, if too many Nans, we don't interpolate and just skip it, so we avoid that 10 minute timepoint
- Then for each channel and each patient and each band: create timeseries where each point is the 10-minute average power (each band), 10-minute exponent (FOOOF), and 10-minute offset (FOOOF). We then z-score each series, interpolate, and pwelch that series specifically to find the 24 hour power (need to interpolate because can't have NaNs for pwelch). Save out 24hr power for each band power, each offset, each exponent

    