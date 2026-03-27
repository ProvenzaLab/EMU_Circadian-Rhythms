#!/bin/bash

#SBATCH --mem=120GB
#SBATCH --job-name=ns5
#SBATCH --time=5-00:00:00
#SBATCH --output=logs1/%x_%j.out
#SBATCH --error=logs1/%x_%j.err
#SBATCH --array=0-2132

python 0_parse_ns5_file.py $SLURM_ARRAY_TASK_ID