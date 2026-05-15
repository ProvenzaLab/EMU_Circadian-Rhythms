#!/bin/bash
#SBATCH --mem=120G
#SBATCH --job-name=01
#SBATCH --partition=chipmunk,guppy,mammoth
#SBATCH --time=1-00:00:00
#SBATCH --output=logs7/%x_%j.out
#SBATCH --error=logs7/%x_%j.err
#SBATCH --array=0-21

python combine_npy_for_deeplearning.py $SLURM_ARRAY_TASK_ID
