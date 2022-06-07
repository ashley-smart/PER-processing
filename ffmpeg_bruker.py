# to get individual jpegs for bruker videos on sherlock

## this should make new directories and run ffmpeg

import os
import subprocess
import sys

#variables to change
date = '20210802'    #date folder

#main path
video_path = '/oak/stanford/groups/trc/data/Ashley2/bruker videos/' + str(date) +'/'   #should end in /



def main():
  #find fly folders
  for fly_dir in os.listdir(video_path):
    if 'fly' in fly_dir:
        fly_video_path = os.path.join(video_path, fly_dir)
        video_name = os.listdir(fly_video_path)
        print(fly_video_path)
        print(video_name)
        if len(video_name) > 1:
            raise Exception("ERROR: THERE ARE TOO MANY ITEMS IN FOLDER", video_name)
        if '.avi' not in video_name[0]:
            raise Exception ("ERROR: this file is not avi", video_name[0])
        fly_video = os.path.join(fly_video_path, str(video_name[0]))

        # make jpeg path
        jpeg_path = os.path.join(video_path, 'analysis/', fly_dir)
        make_dirs(jpeg_path)
        print(jpeg_path)
        
        ## run ffmpeg
        
        final_jpeg_path_v1 = os.path.join(jpeg_path, 'V01frame_%07d.jpg')
        cmd = f'ffmpeg -i REPLACEPATH REPLACEPATHJPEG -hide_banner -loglevel error'  #have to do it this way because I have spaces in the filepath
        split_version = cmd.split(" ")
        split_version[2] = fly_video #replaces REPLACEPATH
        split_version[3] = final_jpeg_path_v1 #replaces REPLACEPATHJPEG
        subprocess.call(split_version)
        
        print(f"{fly_dir} DONE from {date}")
        
        
    
    
    
  
## functions ##
def make_dirs (file_path):
    """this will check if a filepath exists and if it doesn't it will create one"""
    if os.path.exists(file_path):
        print('jpeg directory already exists', file_path)
    else:
        os.makedirs(file_path)
        print('file path created: ', file_path)




if __name__=='__main__':
  main()
