pipeline:
 - parse_data_into_npy.py -> ns3 -> npy blocks of continuous individual ns3 files
 - concat_patient_data.py -> npy blocks -> 10 min ch-wise npy blocks in chunks_out_fixed
 - compute_power.py -> csv files in "chunks_power" separated by channels + patients
 - compute_circadian_power.py -> "circ_power" .pkl files and "figures"
- combine_circ_power.py -circ_power/circadian_power_24hr_summary.csv 
- 


files that failed:
 - /mnt/datalake/data/emu/YFBDatafile/DATA/20240507-140543/NSP1-20240507-140543-004.ns3
 - /mnt/datalake/data/emu/YFFDatafile/DATA/20240820-124851/NSP1-20240820-124851-120.ns3
 - /mnt/datalake/data/emu/YFGDatafile/DATA/20240927-145227/NSP1-20240927-145227-006.ns3
 - /mnt/datalake/data/emu/YFGDatafile/DATA/20240927-145227/NSP1-20240927-145227-008.ns3
 - /mnt/datalake/data/emu/YFGDatafile/DATA/20240927-145227/NSP1-20240927-145227-009.ns3
 - /mnt/datalake/data/emu/YFGDatafile/DATA/20240926-101434/NSP1-20240926-101434-138.ns3
 - /mnt/datalake/data/emu/YFHDatafile/DATA/20241002-085725/NSP1-20241002-085725-017.ns3
 - /mnt/datalake/data/emu/YFHDatafile/DATA/20241003-090840/NSP1-20241003-090840-001.ns3
 - /mnt/datalake/data/emu/YFIDatafile/DATA/20241017-105609/NSP1-20241017-105609-011.ns3
 - /mnt/datalake/data/emu/YFIDatafile/DATA/20241017-134753/NSP1-20241017-134753-059.ns3
 - /mnt/datalake/data/emu/YFIDatafile/DATA/20241018-112807/20241018-112807-003.ns3
 - /mnt/datalake/data/emu/YFKDatafile/DATA/20250213-111216/NSP1-20250213-111216-140.ns3
 - /mnt/datalake/data/emu/YFMDatafile/DATA/20250313-095037/NSP1-20250313-095037-147.ns3 
 - /mnt/datalake/data/emu/YFQDatafile/DATA/20250612-102311/NSP1-20250612-102311-130.ns3
 - /mnt/datalake/data/emu/YFUDatafile/DATA/20251211-131720/NSP1-20251211-131720-120.ns3
 - /mnt/datalake/data/TRD-43036/DBSTRD011/NEURAL/20240720-071633/20240720-071633-001.ns3
