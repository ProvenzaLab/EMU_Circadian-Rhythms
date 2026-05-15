#!/bin/bash

#SBATCH --mem=600GB
#SBATCH --job-name=ns5
#SBATCH --partition=guppy,chipmunk,mammoth
#SBATCH --time=5-00:00:00
#SBATCH --output=logs3/%x_%j.out
#SBATCH --error=logs3/%x_%j.err
#SBATCH --array=0-21

python parse_data_into_npy.py $SLURM_ARRAY_TASK_ID
