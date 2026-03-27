#!/bin/bash

#SBATCH --mem=120GB
#SBATCH --job-name=ns5
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --cpus-per-task=20
#SBATCH --array=1-999%1

# Activate venv
source ~/venvs/emu_env/bin/activate

export TMPDIR=/scratch/$USER/tmp
mkdir -p "$TMPDIR"

export PYTHONPATH=/mnt/labworlds/Provenza/EMU_Circadian-Rhythms:$PYTHONPATH

python parse_data_into_npy_TRD.py $SLURM_ARRAY_TASK_ID