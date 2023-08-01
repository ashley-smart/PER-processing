# import stuff
import peaks #my library

import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint
import os
os.listdir(os.getcwd())
import csv as csv
import json as json
import scipy as scipy
from scipy.signal import find_peaks
import h5py


##### get paths ##########
date = '20230616'
fly_id_date_code = f'b-{date[-4:]}' ##'b-0407'

#Path = 'G:/bruker vid 2023/20230407/results/'  #path to results files from read ROIs or DLC
Path = f'E:/bruker_vid_2023/{date}/results/'  #path to results files from read ROIs or DLC

SavePath = Path + 'h5_files/'
peaks.make_dirs(SavePath)


####   mostly static variables  ########
data_reducer = 100
voltage_framerate = 10000/data_reducer #frames/s # 1frame/.1ms * 1000ms/1s = 10000f/s
#with reducer i get 1 frame for every .1 * 100 ms => frame/.1*100 ms * 1000ms/s = 100f/s
#each "frame" is 0.1ms

## for older videos the video framerate should hve been 200 #f/s, now 5-4 date it appears to be 38.02 f/s (calculated by figuring out frames between 20s light flashes)
video_framerate = 38   
#video_framerate_downstairs = 33




#####  import data  ###
#(allow for bruker light data or video light data)
#(also allow for video PER data and DLC per data)

#check for voltage file -> trigger voltage reading of light
#store the data in an h5py file with the fly # as the key 
# so I don't have to worry about aligning the PER and the light in the same order
#

files = os.listdir(Path)
voltage_files = peaks.check_for_voltage_file(Path)
roi_files = peaks.check_for_results_file(Path)

##look at voltage and roi files and add data to h5 file based on fly#
if roi_files is not None:
    for roi_file in roi_files:
        fly_number = peaks.find_fly_number(roi_file)
        h5_filename = f'{date}_fly_number_{fly_number}_.h5'
        h5_Path = os.path.join(SavePath, h5_filename)
        data = peaks.import_roi_results(os.path.join(Path, roi_file))
        peaks.add_to_h5(h5_Path, 'roi data', data)
        if peaks.check_for_key(h5_Path, 'fly-id') == False:
            fly_id = f'{fly_id_date_code}-{fly_number}'
            peaks.add_to_h5(h5_Path, 'fly-id', fly_id)
        

if voltage_files is not None:
    for voltage_file in voltage_files:
        fly_number = peaks.find_fly_number(roi_file)
        h5_filename = f'{date}_fly_number_{fly_number}_.h5'
        h5_Path = os.path.join(SavePath, h5_filename)
        data = peaks.import_voltage_data(os.path.join(Path, roi_file))
        peaks.add_to_h5(h5_Path, 'voltage data', data)
        if peaks.check_for_key(h5_Path, 'fly-id') == False:
            fly_id = f'{fly_id_date_code}-{fly_number}'
            peaks.add_to_h5(h5_Path, 'fly-id', fly_id)


#set framerate
 # **!!  change so code just asks is voltage framerate or video framerate needed


#set interval time
##since most of my experiments are switch do I need this?
interval_time = None ##decide if I should change this later

#set fly numbers 
# #(should be set when import data)


#get peaks for light and PER
##look at every flies h5 file and open and run peaks 
#    (note: some light data may be in roi file)
#  if there is more than one mean in the data then it will return a list of list of peaks for each mean

h5files = [file for file in os.listdir(SavePath) if '.h5' in file]

#calculate peaks and save to h5 (as well as peaks/sec)
for fly in h5files:
    each_path = os.path.join(SavePath, fly)
    with h5py.File(each_path, 'a') as f:
        if 'roi data' in f.keys():
            framerate = video_framerate
            roi_data = f['roi data'][()]
            print(roi_data[0:10])
            if 'light' in str(roi_data[0][0]):
                print('has light')
            print(np.shape(roi_data))
            data_peaks, properties, columns = peaks.get_peaks(roi_data, each_path, framerate)
            peaks.add_to_h5(each_path, 'roi peak left bases', properties['left_bases'])
            peaks.add_to_h5(each_path, 'roi peak prominences', properties['prominences'])
            peaks.add_to_h5(each_path, 'video framerate', video_framerate)
            
        if 'voltage data' in f.keys():
            framerate = voltage_framerate
            voltage_data = f['voltage data'][()]
            voltage_peaks, voltage_properties, voltage_columns = peaks.get_peaks(voltage_data, each_path, framerate)
            peaks.add_to_h5(each_path, 'voltage peak left bases', voltage_properties['left_bases'])
            peaks.add_to_h5(each_path, 'voltage peak prominences', voltage_properties['prominences'])
            peaks.add_to_h5(each_path, 'voltage framerate', voltage_framerate)



## to run onsets
# 1. get indices where there is a decrease (smoothed_decrease index)
# 2. see if the onset is within 50 frames of a peak and if so append it to the list



# for fly in h5files:
#     each_path = os.path.join(SavePath, fly)
#     with h5py.File(each_path, 'a') as f:
#         print(f.keys())
#         #use onsets to get PER to light

#         #should I smooth it?





# ##find peak onsets

# PER_onsets_matrix_sec = get_onsets_matrix(PER_peaks_sec, data, PER_columns, identifier = 'PER')
# light_onsets_matrix_sec = get_onsets_matrix(light_peaks_sec, light_data[data_index], light_columns, identifier = 'light')
# light_onset_indices = light_peak_properties['left_bases']
# PER_onset_indices = PER_peak_properties['left_bases']


##make plots








#smooth PER peaks 






#find onset of PER peaks



#find indiv






#