#!/bin/bash

#SBATCH --mem=64GB
#SBATCH --job-name=ns5
#SBATCH --time=24:00:00
#SBATCH --output=logsJ/%x_%j.out
#SBATCH --error=logsJ/%x_%j.err
#SBATCH --cpus-per-task=10

set -euo pipefail

source /scratch/altmanrj/venvs/emu_env/bin/activate

export PYTHONPATH=/mnt/labworlds/Provenza/EMU_Circadian-Rhythms #this is for finding imports

cd /mnt/labworlds/Provenza/EMU_Circadian-Rhythms
python AddAtlasLabels.py