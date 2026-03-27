#!/bin/bash

#SBATCH --mem=120GB
#SBATCH --job-name=ns5
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --cpus-per-task=4
#SBATCH --array=1-999%5

# Activate venv
source ~/venvs/emu_env/bin/activate

export TMPDIR=/scratch/$USER/tmp
mkdir -p "$TMPDIR"

export PYTHONPATH=/mnt/labworlds/Provenza/EMU_Circadian-Rhythms:$PYTHONPATH

python 0_parse_ns5_file_TRD.py $SLURM_ARRAY_TASK_ID