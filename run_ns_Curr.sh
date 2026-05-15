#!/bin/bash

#SBATCH --mem=120GB
#SBATCH --job-name=ns5
#SBATCH --time=48:00:00
#SBATCH --output=logsJ/%x_%j.out
#SBATCH --error=logsJ/%x_%j.err
#SBATCH --cpus-per-task=40

set -euo pipefail

source /scratch/altmanrj/venvs/emu_env/bin/activate

export PYTHONPATH=/mnt/labworlds/Provenza/EMU_Circadian-Rhythms #this is for finding imports

cd /mnt/labworlds/Provenza/EMU_Circadian-Rhythms
python continuous_file_processing.py