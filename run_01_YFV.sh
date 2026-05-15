#!/bin/bash
#SBATCH --mem=25G
#SBATCH --job-name=01-YFV
#SBATCH --partition=chipmunk
#SBATCH --time=1-00:00:00
#SBATCH --output=logs5/%x_%j.out
#SBATCH --error=logs5/%x_%j.err

python 1_concat_patient_data.py 18
