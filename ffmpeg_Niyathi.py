## this should make new directories and run ffmpeg

import os
import subprocess
import sys

#variables to change
date = '1-3-22'    #date folder
video_1_name = "Basler acA2440-35um (22467982)_20220103_192741565.m4v"     #include .avi or .m4v
video_2_name = None  #change if have two videos for the same day

#check to make sure this is right, but should work as long as your file structure doesn't change
video_1_path = '/oak/stanford/groups/trc/data/Niyathi/' + str(date) +'/'   #path to video 1, should end in /
video_2_path = None #'/oak/stanford/groups/trc/data/Niyathi/' + str(date) +'/' #change if have two videos

#should not need to change these as long as the video_1_path is correct
video_1_jpeg_path = os.path.join(video_1_path, 'analysis/Video_1/')     #path where should save jpegs should end in /
video_2_jpeg_path = None  #os.path.join(video_1_path, 'analysis/Video_2/') #change if have two videos

def main():
  #make jpeg directories
  make_dirs(video_1_jpeg_path)
  if video_2_name is not None: 
    make_dirs(video_2_jpeg_path)
  
  #run ffmpeg code
  final_jpeg_path_v1 = os.path.join(video_1_jpeg_path, 'V01frame_%07d.jpg')
  final_vid_1_path = os.path.join(video_1_path, video_1_name)
  cmd = f'ffmpeg -i REPLACEPATH REPLACEPATHJPEG'  #have to do it this way because I have spaces in the filepath
  split_version = cmd.split(" ")
  split_version[2] = final_vid_1_path
  split_version[3] = final_jpeg_path_v1
  subprocess.call(split_version)
  
  if video_2_name is not None:
    final_jpeg_path_v2 = os.path.join(video_2_jpeg_path, 'V02frame_%07d.jpg')
    final_vid_2_path = os.path.join(video_2_path, video_2_name)
    cmd = f'ffmpeg -i REPLACEPATH REPLACEPATHJPEG'  #have to do it this way because I have spaces in the filepath
    split_version = cmd.split(" ")
    split_version[2] = final_vid_2_path
    split_version[3] = final_jpeg_path_v2
    subprocess.call(split_version)
  
  
  
## functions ##
def make_dirs (file_path):
    """this will check if a filepath exists and if it doesn't it will create one"""
    if os.path.exists(file_path):
        print('jpeg directory already exists', file_path)
    else:
        os.makedirs(video_1_jpeg_path)
        print('file path created: ', file_path)




if __name__=='__main__':
  main()
