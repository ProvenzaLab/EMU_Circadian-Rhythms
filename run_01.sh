#!/bin/bash
#SBATCH --mem=120GB
#SBATCH --job-name=01
#SBATCH --partition=guppy,chipmunk
#SBATCH --time=2-00:00:00
#SBATCH --output=logs6/%x_%j.out
#SBATCH --error=logs6/%x_%j.err
#SBATCH --array=0-21

python 1_concat_patient_data.py $SLURM_ARRAY_TASK_ID
