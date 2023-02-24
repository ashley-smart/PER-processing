import math
import csv 
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import path
import scipy as scipy
import scipy.io
import cv2

import os
os.listdir(os.getcwd())

import json as json
import pickle as pickle

from read_roi import read_roi_file
from read_roi import read_roi_zip

## Stuff to change  ##

dates = ['20210702', '20210607', '20210714', '20210716', '20210719']

def main():
    for date in dates:
        print(f"RUNNING CURRENT DATE: {date}")
        roi_path = "/D:/" + str(date) + "/analysis/"  ##JPEGS AND ROIS MUST BE SAVED IN SEPERATE ANALYSIS FOLDER
        ##jpegs must have "frames" in the folder name
        ## ROI folder must have "ROI" in the name
        
        ##I saved my jpegs as "flyname+condition"_frames
        ##ROIS are either a folder if they have light or just PER if they didn't have light (I need an option for either)
        
        #look for results files and roi files
        fly_number_done = []
        roi_list = []
        for file in os.listdir(roi_path):
            if 'Results' in file:
                fly_number = find_number(file)
                fly_number_done.append(fly_number)
            elif 'roi' in file or 'ROI' in file:
                roi_list.append(file)

        for fly_dir in os.listdir(roi_path):
            #this will clear out if results are already done for that fly and if it is a PER (roi)
            if not any(str(number) in fly_dir for number in fly_number_done) and 'fly' in fly_dir and 'ROI' not in fly_dir and 'PER' not in fly_dir: #to get fly folders without getting rois  #previously saved as PER
                print('fly dir is ok:', fly_dir)
                dir_number = find_number(find_fly_string(fly_dir))
                print('fly dir number:', dir_number)
                if len(dir_number) == 0:
                    raise Exception(f"ERROR: THERE IS NO DIRECTORY NUMBER FOR...{fly_dir}")
                print('roi path:', roi_path)
                print('fly dir:', fly_dir)
                
                jpeg_path = os.path.join(roi_path, fly_dir)
                
                print('jpeg path', jpeg_path)
                #since rois are different for every video specify with fly tag same as fly dir name
                #this may need to be changed when I get more than one ROI per fly
                #determine ROI name
                #there may be more numbers because of date => look only at part of string after "fly" could be fly2_PER or fly_2.roi etc
                for roi_file in roi_list:
                    post_fly_string = find_fly_string(roi_file)
                    if dir_number in post_fly_string:
                        roi_name = roi_file
                    else:
                        raise Exception(f"could not find roi file for {fly_dir}")
                        continue             
                print('roi_name:', roi_name)
                save_file_name = "Results_video_" + str(fly_dir) + "_python.csv" #so each fly is saved seperately
                save_path = "/oak/stanford/groups/trc/data/Ashley2/bruker videos/" + str(date) + "/analysis/" 
                make_dirs(save_path)

                if os.path.exists(jpeg_path):
                  jpeg_file_names = os.listdir(jpeg_path)
                  sorted_jpeg_file_names = sorted(jpeg_file_names)
                  print('sorted', sorted_jpeg_file_names[0:5])

                  ######################################################

                  ## get ROI dictionaries
                  #read_roi_file puts data into dict in dict
                  all_roi_info_dict = []                 
                  roi_file_path = os.path.join(roi_path, roi_name)
                  if roi_name not in os.listdir(roi_path):
                    raise Exception (f"ERROR: Roi name ({roi_name}) is not found in directory: {os.listdir(roi_path)}")
                    break
                  roi = read_roi_file(roi_file_path)
                  all_roi_info_dict.append(roi)

                  #get roi names as keys for original dict that has dicts of info
                  #need to use list to get rid of dict specifier
                  roi_names_as_keys = []
                  for i in range(len(all_roi_info_dict)):
                      roi_key_name = list(all_roi_info_dict[i].keys())
                      roi_names_as_keys.append(roi_key_name[0])
                  print(roi_names_as_keys)

                  all_x1 = []
                  all_y1 = []
                  all_width = []
                  all_height = []
                  all_name = []
                  all_poly_name = []
                  all_poly_x = []
                  all_poly_y = []
                  all_name_for_header = []

                  for i in range(len(all_roi_info_dict)):
                      if all_roi_info_dict[i][roi_names_as_keys[i]]['type'] == 'rectangle':
                          x1 = all_roi_info_dict[i][roi_names_as_keys[i]]['left']
                          y1 = all_roi_info_dict[i][roi_names_as_keys[i]]['top']
                          height = all_roi_info_dict[i][roi_names_as_keys[i]]['height']
                          width = all_roi_info_dict[i][roi_names_as_keys[i]]['width']

                          #convert rectangle info to the same format as the polygon (xxxx) (yyyy) order for polygon is lower right then counterclockwise
                          right_x = x1 + width
                          lower_y = y1 + height #(y runs opposite expected, 0 is top, high is bottom)
                          poly_x = (right_x, right_x, x1, x1) #order = lower right, upper right, upper left, lower left
                          poly_y = (lower_y, y1, y1, lower_y) #order = lower right, upper right, upper left, lower left

                      if all_roi_info_dict[i][roi_names_as_keys[i]]['type'] == 'polygon':
                          poly_x = all_roi_info_dict[i][roi_names_as_keys[i]]['x']
                          poly_y = all_roi_info_dict[i][roi_names_as_keys[i]]['y']

                      poly_name = all_roi_info_dict[i][roi_names_as_keys[i]]['name']
                      name_for_header = "Mean(" + str(poly_name.replace("'", " ")) + ")"
                      print(name_for_header)
                      all_poly_name.append(poly_name)
                      all_poly_x.append(poly_x)
                      all_poly_y.append(poly_y)
                      all_name_for_header.append(name_for_header)

                  #get some frames to calc h, w
                  all_frames = []
                  for jpeg in sorted_jpeg_file_names[0:10]:
                      if '.jpg' in jpeg:
                         jpeg_file_path = os.path.join(jpeg_path, jpeg)
                         frame = cv2.imread(jpeg_file_path, 0) #0 to load in grayscale
                         all_frames.append(frame)
                  h,w = np.shape(all_frames[0])  #add c if it is not in grayscale

                  #convert pixels in image into coordinates in an array
                  xv, yv = np.meshgrid(np.arange(0,w,1), np.arange(0,h,1))

                  #turn polygon roi into a path and see which pixels are inside of it
                  all_roi_coordinates = []
                  all_roi_paths = []
                  all_roi_masks = []
                  for roi_index in range(len(all_poly_x)):
                      x = all_poly_x[roi_index]
                      y = all_poly_y[roi_index]
                      roi_coordinates = list(zip(x,y))
                      print(roi_coordinates)
                      all_roi_coordinates.append(roi_coordinates)
                      ### NEED TO ADD LIGHT too, rectangle shape

                      #convert poly coords to path
                      #for poly_point_index in range(len(x)): #some polygons are 4 or 5 vertices
                      roi_path = path.Path(roi_coordinates)
                      all_roi_paths.append(roi_path)
                      roi_mask = np.where(roi_path.contains_points(np.hstack((xv.flatten()[:,np.newaxis],yv.flatten()[:,np.newaxis]))))
                      all_roi_masks.append(roi_mask)  

                  #cannot store all the data at once so 
                  #open each frame-find the itnensity in the ROI 
                  #and save the average intensity for each frame
                  all_avg_intensity = []
                  for jpeg_index in range(len(sorted_jpeg_file_names)):
                      if '.jpg' in sorted_jpeg_file_names[jpeg_index]:
                         #open each frame to get instensities
                         jpeg_file_path = os.path.join(jpeg_path, sorted_jpeg_file_names[jpeg_index])
                         frame = cv2.imread(jpeg_file_path, 0) #0 to load in grayscale
                         if frame is not None:
                             #frame = cv2.imread(jpeg_file_path) 
                             #flatten image to use mask on it
                             flat_frame = frame.flatten()
                             #get averages for all ROI in one list
                             all_roi_avg_intensity_per_frame = []
                             for roi_index in range(len(all_roi_masks)):
                                 avg_intensity_each_roi = np.mean(flat_frame[all_roi_masks[roi_index]])
                                 all_roi_avg_intensity_per_frame.append(avg_intensity_each_roi)
                         else:
                             print(jpeg_index)
                         all_avg_intensity.append(all_roi_avg_intensity_per_frame)

                  #save results 
                  #want the format to be the same as the fiji format so I don't have to change my other code
                  #format for fiji is row 1 [blank(col of frame numbers), Label, Mean(PER), Mean(PER2), etc]
                  header = all_name_for_header

                  with open(os.path.join(save_path, str(save_file_name)), 'w', newline='') as csvFile:
                      writer = csv.writer(csvFile)
                      writer.writerow(header)
                      for frame_i in range(len(all_avg_intensity)):
                          writer.writerow(all_avg_intensity[frame_i])
                  print(str(date) + ' fly:' + str(fly_dir) + ' ----------- COMPLETED AND SAVED!') 
                else:
                    print(f'{jpeg_path} does not exist')
                    continue


## functions ##
def make_dirs (file_path):
    """this will check if a filepath exists and if it doesn't it will create one"""
    if os.path.exists(file_path):
        print('jpeg directory already exists', file_path)
    else:
        os.makedirs(file_path)
        print('file path created: ', file_path)
        
def find_number(string):
    """want this to give number but if split with non-number character to stop. This will give just the first number it finds"""
    number = ""
    for i in range(len(string)):
        current_character = string[i]      
        if current_character.isdigit():
            number = number + current_character 
            if i != len(string)-1: #if it's not the last character
                next_character = string[i+1]
                if not next_character.isdigit():
                    break
    return number
                    
def find_fly_string(string):
    """things after fly will be returned as string"""
    post_fly_string = string.split("fly",1)[1]
    return post_fly_string




if __name__=='__main__':
  main()
