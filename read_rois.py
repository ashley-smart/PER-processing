## this is for behavior ROIS

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



##  NOTE:  before running this code make sure there is an ROI folder and it is UNZIPPED!


#### change this ####
#print('got this far')
date = '3-28-22'  #name of folder the files are in 
video_number = 1   # video number using
roi_number = 1 #make sure rois are saved with this filename format "RoiSet_vid1"
path_to_date = '/oak/stanford/groups/trc/data/Niyathi/' ##end with / and just before date folder (shouldn't need to change)
   
###   ###

roi_path = str(path_to_date) + str(date) + '/analysis/RoiSet_vid' + str(roi_number) + "/"
rois = os.listdir(roi_path)

jpeg_path = str(path_to_date) + str(date) + "/analysis/Video_" + str(video_number) + "/"
jpeg_file_names = os.listdir(jpeg_path)
print('unsorted', jpeg_file_names[0:5])
sorted_jpeg_file_names = sorted(jpeg_file_names)
print('sorted', sorted_jpeg_file_names[0:5])

# location to save csv files 
save_path = str(path_to_date) + str(date) + "/analysis/" 

#name of file when completed (keep this the same)
save_file_name = "Results_video_" + str(video_number) + "_python_sorted.csv"

if os.path.exists(save_path):
    print('save path folder there')
else:
    os.makedirs(save_path)
    print('save path folder created')
    
    
    
######################################################
    
    
    
## get ROI dictionaries
#read_roi_file puts data into dict in dict
all_roi_info_dict = []
for roi_name in rois:
    roi_file_path = os.path.join(roi_path, roi_name)
    print(roi_file_path)
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
