#!/bin/bash

#SBATCH --mem=300GB
#SBATCH --partition=chipmunk
#SBATCH --job-name=ns5
#SBATCH --time=2-00:00:00
#SBATCH --output=logs2/%x_%j.out
#SBATCH --error=logs2/%x_%j.err
#SBATCH --array=15-21

python parse_data_into_npy.py $SLURM_ARRAY_TASK_ID
