#!/bin/bash
#SBATCH --job-name=3-25IIread_rois
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --partition=owners
#SBATCH --cpus-per-task=4
#SBATCH --output=./roi-logs/mainlog.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

ml python/3.6.1

date
python3 -u /home/users/asmart/projects/PER-processing/read_rois.py
