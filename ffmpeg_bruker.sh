#!/bin/bash
#SBATCH --job-name=ffmpeg
#SBATCH --time=4-00:00:00
#SBATCH --ntasks=1
#SBATCH --partition=trc
#SBATCH --cpus-per-task=2
#SBATCH --output=./logs/mainlog2.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

ml python/3.6.1
ml system
ml ffmpeg

date
python3 -u /home/users/asmart/projects/PER-processing/ffmpeg_bruker.py
