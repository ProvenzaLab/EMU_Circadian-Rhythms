#!/bin/bash

#SBATCH --mem=120GB
#SBATCH --job-name=ns5
#SBATCH --time=24:00:00
#SBATCH --output=logsNew/%x_%j.out
#SBATCH --error=logsNew/%x_%j.err
#SBATCH --cpus-per-task=20

set -euo pipefail

source ~/venvs/emu_env/bin/activate

export TMPDIR=/mnt/labworlds/Provenza/tmp
mkdir -p "$TMPDIR"

export PYTHONPATH=/mnt/labworlds/Provenza/EMU_Circadian-Rhythms #this is for finding imports

python continuous_file_processing.py