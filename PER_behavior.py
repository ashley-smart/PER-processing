
## rewriting scipy peaks with a library


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
date = '20230407'
fly_id_date_code = 'b-0407'

Path = 'G:/bruker vid 2023/20230407/results/'  #path to results files from read ROIs or DLC
SavePath = Path + 'h5_files/'
peaks.make_dirs(SavePath)


####   mostly static variables  ########
data_reducer = 100
voltage_framerate = 10000/data_reducer #frames/s # 1frame/.1ms * 1000ms/1s = 10000f/s
#with reducer i get 1 frame for every .1 * 100 ms => frame/.1*100 ms * 1000ms/s = 100f/s
#each "frame" is 0.1ms
video_framerate = 200 #f/s
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

for fly in h5files:
    each_path = os.path.join(SavePath, fly)
    with h5py.File(each_path, 'a') as f:
        if 'roi data' in f.keys():
            roi_data = f['roi data'][()]
            print(roi_data[0:10])
            if 'light' in str(roi_data[0][0]):
                print('has light')
            print(np.shape(roi_data))
            data_peaks, properties, columns = peaks.get_peaks(roi_data, each_path)
        if 'voltage data' in f.keys():
            voltage_data = f['voltage data'][()]
            light_peaks, light_properties, columns = peaks.get_peaks(roi_data, each_path)



##make plots








#smooth PER peaks 






#find onset of PER peaks



#find indiv






#