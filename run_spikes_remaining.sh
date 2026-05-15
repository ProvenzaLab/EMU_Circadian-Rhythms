#!/bin/bash
#SBATCH --mem=300GB
#SBATCH --job-name=ns5_spikes_remaining
#SBATCH --cpus-per-task=20
#SBATCH --partition=guppy,chipmunk,mammoth
#SBATCH --time=7-00:00:00
#SBATCH --qos=big_batch_tier
#SBATCH --output=logs2/%x_%j.out
#SBATCH --error=logs2/%x_%j.err
#SBATCH --array=0-5785

python parse_data_into_spikes_remaining.py $SLURM_ARRAY_TASK_ID
