#!/bin/bash
#SBATCH --mem=350GB
#SBATCH --job-name=ns5_spikes
#SBATCH --cpus-per-task=20
#SBATCH --partition=guppy,chipmunk,mammoth
#SBATCH --time=7-00:00:00
#SBATCH --qos=big_batch_tier
#SBATCH --output=logs3/%x_%j.out
#SBATCH --error=logs3/%x_%j.err
#SBATCH --array=21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0

python parse_data_into_npy_spikes.py $SLURM_ARRAY_TASK_ID
