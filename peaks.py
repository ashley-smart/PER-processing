##library for PER_behavior

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



## general functions
def make_empty_h5(savefile, key, dims):
    """make empty h5 file with specified key and dims as the shape. returns the filename"""
    with h5py.File(savefile, 'w') as f:
        dset = f.create_dataset(key, dims, dtype='float32', chunks=True)
    return savefile

def add_to_h5(Path, key, value):
    """adds new key value to h5 file and checks if it already exists
    does overwrite"""
    with h5py.File(Path, 'a') as f:
        if key not in f.keys(): #check if key already in file
            f[key] = value
        else:
            del f[key]
            #print('deleting old key and OVERWRITING')
            f[key] = value

def check_for_key(h5Path, key):
    """returns true if key to h5file path exists
    args:
        h5Path = path to h5 file
        key = string want to look for
    returns:
        True if found key
        False if key doesn't exist in file
        """
    with h5py.File(h5Path, 'r') as f:
        if key in f.keys():
            return True
        else:
            return False

def make_dirs(Path):
    """make folder if it doesn't already exist"""
    if not os.path.isdir(Path):
        os.mkdir(Path)

## set-up functions (import and organize data)
def check_for_voltage_file (Path):
    """looks in path for voltage files and returns it/them. otherwise returns None. 
    if more than one it will return all"""
    files = os.listdir(Path)
    all_voltage = []
    for file in files:
        if '.csv' in file and 'Voltage' in file:
            all_voltage.append(file)
    if len(all_voltage) > 0:
        return all_voltage
    else:
        return None
    
def check_for_results_file (Path):
    """looks in path for Results files and returns it/them. otherwise returns None. 
    if more than one it will return all"""
    files = os.listdir(Path)
    all_results = []
    for file in files:
        if '.csv' in file and 'Results' in file:
            all_results.append(file)
    if len(all_results) > 0:
        return all_results
    else:
        return None
    

def import_voltage_data (voltage_path, data_reducer = 100):
    """takes a single voltage file path and returns a list of the voltage data. 
    Reduces the data by data reducer amount (every data_reducer(th) element is taken 
    and the rest is ignored). Default data_reducer number = 100"""
    if "Voltage" not in voltage_path:
        print("Caution: this file: {voltage_path} does not contain 'Voltage', make sure it's the right file")
    light_data = []
    with open(os.path.join(voltage_path), 'r') as raw_volt:
        data_single = []
        volt_reader = csv.reader(raw_volt)
        for i, row in enumerate(volt_reader):
            if i % data_reducer == 0:  #this will downsample the data by taking every 100, i % 100 means will divide i by 100 and take the ones that have no remainder
                data_single.append(row)
        light_data.append(data_single)
    return light_data

def import_roi_results (results_path):
    """takes results filepath and returns a list of all the data in the file"""
    with open(os.path.join(results_path), 'r') as rawfile:  #'rb' in python2
        data_single = []
        reader = csv.reader(rawfile)
        data_single = list(reader)
    return data_single


def find_fly_number(file):
    """takes string, looks for fly and then the number following "fly" returns the number"""
    fly_number = find_number(find_fly_string(file))
    return fly_number


def find_number(string, dash = 'n'):
    """want this to give number but if split with non-number character to stop. This will give just the first number it finds unless dash = 'y' then it will include the next 3 characters"""
    number = ""
    for i in range(len(string)):
        current_character = string[i]      
        if current_character.isdigit():
            number = number + current_character 
            if i != len(string)-1: #if it's not the last character
                next_character = string[i+1]
                if not next_character.isdigit():
                    if dash == 'n':
                        break
                    else:
                        if next_character == '-':
                            number = number + string[i+1:i+4]
                            break
    return number
                    
def find_fly_string(string):
    """things after fly will be returned as string"""
    post_fly_string = string.split("fly",1)[1]
    return post_fly_string

## probably change this. I don't think I want "asks" anymore
def get_intervals_and_asks(list_map, file_name_list):
    """Get the PER interval and the ask type for each file in file_name_list.
    
    Args:
      list_map: A Dict of {interval: [list of filenames]} where interval is either the
        length of the interval in seconds or one of the strings {'random', 'none'}.
      file_name_list: A List of string filenames. The order determines the order of the output.
    Returns:
      A tuple of lists (interval_ms_list, ask) ordered to match file_name_list.
      interval_ms_list: a list of the interval length in milliseconds for each result in file_name_list
      ask: a list of ask types: 0 for fixed intervals, 'r' for random, and 'y' for none.
    """
    interval_ms_list = []
    ask = []
    for file_name in file_name_list:
        for key in list_map:
            if file_name in list_map[key]:
                if isinstance(key, str): # using strings to pass special values
                    if key == 'none' or 'y':
                        interval_ms_list.append(0)
                        ask.append('y')
                    if key == 'random':
                        interval_ms_list.append(0)
                        ask.append('r')
                else:  # if the key is not a string, it must be a number.
                    interval_ms_list.append(key * 1000)
                    ask.append(0)
                #print(key, file_name, interval_ms_list[-1], ask[-1]) # optional if you like to print stuff.
    return interval_ms_list, ask

def generate_fly_number_list(date_code, number_flies):
    """Return a list of fly names based on date code
    Args:
        date code: the string that will form the beginning of the fly name (i.e. 150411)
        number_flies: the number of flies need date codes for 
            (can give len(data_all) in current iteration of code)
    Returns:
        list of strings with date_code_# (i.e. 150411-2)"""
    fly_code_list = []
    for i in range(number_flies):
        fly_code = str(date_code) + '-' + str(i+1)
        fly_code_list.append(fly_code)
    return fly_code_list




#### analysis functions
def make_bins (time_range, binsize):
    """to make bins based on desired time range and binsize--using ms
    args: 
        time_range = max time in ms to have bins go until
        binsize = ms per bin
    returns:
        array of bins that extend to timerange and are binsize"""
    ms_binlength = np.asarray(range(int(time_range/binsize) + 1)) * binsize
    return ms_binlength

def is_column_mean (data, row, column):
    """return true if cell contains 'mean' for ROI code or has input or diode from voltage data
    args:
        data: the data for a fly from csv file
        row:  row of data to look in
        column: column of data to look in
    returns: True if finds keyword"""
    
    return "Mean" in str(data[row][column]) or "diode" in str(data[row][column]) or " Input 0" in str(data[row][column]) 


def get_header(data, column_number):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    title_list = []
    """gets header (row 0) for data set for specified column (data, column number)"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        title_list.append(row[column_number])
    titles = np.array(title_list[:1]) #changes the list into a numpy array. [:1] means take the first row
    return titles

def get_diode_column(raw_light_data):
    """light data should be a single fly and have the header be the first row"""
    header = raw_light_data[0]
    diode_column = []
    for i in range(header):
        if "Input 0" in header[i]:
            diode_column = i
    reshape_light_data = np.transpose(raw_light_data[1:])
    column = reshape_light_data[:][diode_column]
    column = [float(i) for i in column]
    return column

def get_mean_titles(data):
    """data is raw data for one fly, returns the titles of every column that has Mean in it"""
    #1. get mean column indices
    mean_indices = get_mean_indices(data)

    #2. get array with titles
    title_collection = []
    for t in mean_indices:
        title_collection.append(get_header(data, t))
    if len(title_collection) > 1:
        mean_titles = np.vstack(title_collection).T
    else:
        mean_titles = title_collection
    return mean_titles

def get_mean_indices(data):
	"""get indices where there are means from data from one fly (previous code this was called mean_column"""
	mean_indices = []
	for row in range(len(data)):
		for column in range(len(data[row])):
			if is_column_mean(data, row, column):
				mean_indices.append(column) #store column index
	return mean_indices

def get_means(data, column_number):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    mean_list = []
    """gets column for (data, column_number) and eliminates the header (row 0) and puts it into a np.array"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        mean_list.append(row[column_number])
    means = np.asarray(mean_list[1:], dtype=float) #changes the list into a numpy array. [1:] means take the second number to the end 
    #(to get rid of the title). dtype changes from strings to np integers
    return means

def is_column_in_list(data, row, column, str_list):
	return str(data[row][column]) in str_list

def is_column_light(data, row, column):
	return is_column_in_list(data, row, column, ("Light", "light", "diode", "Mean(Light)", " Input 0"))




##
def get_peaks(data, h5file,  framerate, override = False, prominence = 3, distance = 15):
    """ uses scipy peaks to find peak points of data 
    finds negative peaks for PER and positive peaks for light. 
    Will also add the peaks to the h5 file of the fly and peaks/s to the h5 file
    args: 
        data = raw data imported that contains a header with "mean", "diode", "input 0"
        h5file = path to h5 file data to save peaks data
        framerate = frames/s or data/s in case of voltage 
        override = False as default. If true then it allows the 
            function to find peaks for data that has no header 
            (will assume it is PER and do negative peaks)
            data must then be a single array
    returns:
        peaks = the indices where there are peaks
        peak_properties = dict of various properties from scipy peaks
        columns = raw data"""
    
    ##look through data and find if there is light or PERs
    #1. get mean column indices and mean titles
    mean_indices = get_mean_indices(data)
    mean_titles = get_mean_titles(data)
    print(f'titles are {mean_titles}')

    if len(mean_indices) < 1:
        if override == True:
            squeeze_column = np.squeeze(data)
            peaks, properties = scipy.signal.find_peaks(squeeze_column*-1, prominence = prominence, distance = distance) 
            return peaks, properties, squeeze_column
        else:
            raise Exception(f'There is no identified mean index--If due to lack of header consider overriding and inputting single array')
        
    #2. find peaks
    all_peaks= []
    columns = [] #needed for boolean onsets later
    for mean_index in range(len(mean_indices)):
        single_column = get_means(data, mean_indices[mean_index])
        #to get each element out of their own array and into one array with all elements
        squeeze_column = np.squeeze(single_column) 
        print(f'current mean title is {mean_titles[0][mean_index]}')
        if is_column_light(mean_titles, 0, mean_index) or 'diode' in str(mean_titles[0][mean_index]) or 'light' in str(mean_titles[0][mean_index]) or 'Input 0' in str(mean_titles[0][mean_index])  or 'Light' in str(mean_titles[0][mean_index]):
            print('light')
            #peaks, _ = scipy.signal.find_peaks(squeeze_column, prominence = .5)
            columns.append(single_column)
            ##modification for noisy diode data
            light_median = np.median(single_column, axis = 0)
            early_light_max = max(single_column[0:2000])
            #peaks, _ = scipy.signal.find_peaks(squeeze_column, height = light_median[0], prominence = .3, distance = 10)
            peaks, properties = scipy.signal.find_peaks(squeeze_column, height = early_light_max +.001, prominence = .1, distance = 10)
            add_to_h5(h5file, 'light peaks', peaks)
            ## get peaks per second rather than frames
            peaks_sec = np.array(peaks) / framerate 
            add_to_h5(h5file, 'light peaks sec', peaks_sec)
        elif 'PER' in str(mean_titles[0][mean_index]):
            print('PER')
            peaks, properties = scipy.signal.find_peaks(squeeze_column*-1, prominence = 3, distance = 15) 
            columns.append(single_column)
            add_to_h5(h5file, 'PER peaks', peaks)
            #distance is req frames between peaks
            ## get peaks per second rather than frames
            peaks_sec = np.array(peaks) / framerate 
            add_to_h5(h5file, 'PER peaks sec', peaks_sec)
        else:
            print(f'Not finding PER or Light for {str(mean_titles[0][mean_index])}')

        all_peaks.append(peaks)
    return all_peaks, properties, columns


def get_voltage_data(dataset_path):
    """gets voltage data from voltage file and 
    returns a list of times and a list of voltage values.
    
    args:
    Path = path to fly (folder that contains brain data and voltage data)
    data_reducer = default 100, to reduce the number of timepoints 
    it gets because the resolution is very high when collected
    
    returns:
    voltage data: list of voltage values (every data reducer amount)
    voltage_time: list of timepoints saved by voltage file"""
    
    #1. get voltage file
    #2. get time column (first column)
    #3. get data column 
    voltage_path = find_voltage_file(dataset_path)
    with open(voltage_path, 'r') as rawfile:
        reader = csv.reader(rawfile)
        data_single = []
#         for i, row in enumerate(reader):
#             if i % data_reducer == 0: #will downsample the data 
#                 data_single.append(row)
        for i, row in enumerate(reader):
            data_single.append(row)
        light_data = data_single    

    light_data_column = get_diode_column(light_data)
    time_data_column = get_time_column(light_data)
    return light_data_column, time_data_column
    
def get_time_column(raw_light_data):
    """light data should be single fly and have the header be the first row"""
    header = raw_light_data[0]
    diode_column = []
    for i in range(len(header)):
        if 'Time(ms)' in header[i]: 
            time_column = i
#         else:
#             print(f'could not find "Time(ms)" in header{header}')
    reshape_light_data = np.transpose(raw_light_data[1:])
    column = reshape_light_data[:][time_column] #don't want header anymore
    column = [float(i) for i in column] #for some reason it was saved as string before
    return column

def find_voltage_file(dataset_path):
    """path should be fly folder. Returns path to specific voltage csv"""
    for name in os.listdir(dataset_path):
        if 'Voltage' in name and '.csv' in name:
            voltage_file = name
            voltage_path = os.path.join(dataset_path, voltage_file)
    return voltage_path


def get_light_peaks (dataset_path): #, data_reducer = 100):
    
    """input fly path and get out the light peaks files in milliseconds"""
#     data_reducer = 100
#     light_data = []
#     voltage_path = find_voltage_file(Path)
#     with open(voltage_path, 'r') as rawfile:
#         reader = csv.reader(rawfile)
#         data_single = []
#         for i, row in enumerate(reader):
#             if i % data_reducer == 0: #will downsample the data 
#                 data_single.append(row)
#         #light_data.append(data_single) #for more than one fly
#         light_data = data_single    
    voltage_multiplier = 0.9991401258909588  ##this is the average of the more accurate estimations of the last bleedthrough time and corresponding light flash in voltage
    #voltage_multiplier = 0.9991021996109531  #this was calculated from bleedthrough and voltage difference on bruker 8.7.23
    light_data_column, time_data = get_voltage_data(dataset_path)

    # find peaks
    light_median = np.median(light_data_column)
    early_light_max = max(light_data_column[0:2000])
    light_peaks, properties = scipy.signal.find_peaks(light_data_column, height = early_light_max +.001, prominence = .1, distance = 10)
    #there is a condition that requires this, but I can't remember exactly what the data looked like
    if len(light_peaks) == 0:
        print("attempting new early_light_max, because no light peaks")
        early_light_max = max(light_data_column[0:100])
        light_peaks, properties = scipy.signal.find_peaks(light_data_column, height = early_light_max +.001, prominence = .1, distance = 10)
        
        if len(light_peaks) == 0:
            print("There are still no light peaks")
            print("skipping this fly--no light peaks")
            
    
#     ## convert to seconds
#     voltage_framerate =  10000/data_reducer #frames/s # 1frame/.1ms * 1000ms/1s = 10000f/s
#     light_peaks_adjusted = light_peaks/voltage_framerate
    
    ##use time to give voltage in time
    ##light_peaks should be the indices of peaks => I can check the indices in time column
    light_peaks = np.array(light_peaks)
    print(np.shape(light_peaks))
    time_data = np.array(time_data)
    light_ms = time_data[light_peaks]*voltage_multiplier

    #save light peaks
    light_peaks_path = os.path.join(dataset_path, 'light_peaks.h5')
    #add_to_h5(light_peaks_path, 'light peaks ms', light_ms)
    
    #get just one peak (will take the last value before the drop)
    single_light_ms = get_single_light_peaks(light_ms, 10000)
    add_to_h5(light_peaks_path, 'light peaks ms', single_light_ms)
    return single_light_ms



def get_single_light_peaks(light_peaks, seperator):
    """takes in array of light peaks and makes sure they are at least seperator distance apart
    args:
    light_peaks = array that has the peaks in it (in ms or s but change seperator)
    seperator = value that two adjacent peaks must be apart in order to be kept. 
    last number that is far enough apart will be kept"""
    diff = light_peaks[1:] - light_peaks[0:-1]
    single_light_peak_indices = np.where(diff>seperator)[0]
    single_light_peaks = light_peaks[single_light_peak_indices]
    return single_light_peaks
#     single_light_peaks = []
#     for i in range(len(light_peaks)-1):
#         current = light_peaks[i]
#         next_time = light_peaks[i+1]
#         if next_time - current > seperator:
#             single_light_peaks.append(current)
#     single_light_peaks = np.array(single_light_peaks)
#     return single_light_peaks



def get_brain_t_switch_set(dataset_path, exp_length1 = 20, exp_length2 = 40):
    """returns array of arrays of switch times that correspond to index in t of brains.
    returns seperately 20 and 40s experiemnts
    20s_t_points = [[start1 stop1] [start 2 stop2]]
    *takes time from zstack timestamps to find which zstack the light is in"""
    
    light_peaks_twenty_times, light_peaks_forty_times = get_times_switch_blocks (dataset_path, exp_length1, exp_length2)
    timestamps = load_timestamps(dataset_path)
    average_timestamps = np.mean(timestamps, axis = 1)/1000  ##to convert ms to s to match light_peaks
    
    first_timestamps = []
    last_timestamps = []
    for t in timestamps:
        first_timestamps.append(t[0])
        last_timestamps.append(t[-1])

    first_timestamps = np.array(first_timestamps)
    first_timestamps_s = first_timestamps/1000
    last_timestamps = np.array(last_timestamps)
    last_timestamps_s = last_timestamps/1000
    
    twenty_switch_set_t = []
    forty_switch_set_t = []
    for switch_set in light_peaks_twenty_times:
        start_time = switch_set[0]
        end_time = switch_set[1]
        
        ##find start time based on z-stack times
        #the last z = 0 timstamp that is less then switch time
        first_index_start = np.where(first_timestamps_s < start_time)[0][-1]
        #last z slice (z = 49) that switch time happens before
        last_index_start = np.where(last_timestamps_s > start_time)[0][0]
        if first_index_start == last_index_start:
            start_time_index = first_index_start
        ##find out if it's in the middle of two stacks
        elif last_timestamps_s[first_index_start] < start_time < first_timestamps_s[last_index_start]:
            ##then it's between timestamps, if start time then have switch start at the following zstack
            start_time_index = last_index_start
        else:
            #this shouldn't happen
            print('odd scenario. not in same z-stack and not between z-stacks')
            
        #end time
        first_index_end = np.where(first_timestamps_s < end_time)[0][-1]
        last_index_end = np.where(last_timestamps_s > end_time)[0][0]
        if first_index_end == last_index_end:
            end_time_index = first_index_end
        elif last_timestamps_s[first_index_end] < end_time < first_timestamps_s[last_index_end]:
            #ending index choose the zstack before (miss the bit between, but I'm removing that data anyway)
            end_time_index = first_index_end
        else:
            #this shouldn't happen
            print('odd scenario. not in same z-stack and not between z-stacks')

        both = (start_time_index, end_time_index)
        twenty_switch_set_t.append(both)

    for switch_set in light_peaks_forty_times:
        start_time = switch_set[0]
        end_time = switch_set[1]
        
        ##find start time based on z-stack times
        #the last z = 0 timstamp that is less then switch time
        first_index_start = np.where(first_timestamps_s < start_time)[0][-1]
        #last z slice (z = 49) that switch time happens before
        last_index_start = np.where(last_timestamps_s > start_time)[0][0]
        if first_index_start == last_index_start:
            start_time_index = first_index_start
        ##find out if it's in the middle of two stacks
        elif last_timestamps_s[first_index_start] < start_time < first_timestamps_s[last_index_start]:
            ##then it's between timestamps, if start time then have switch start at the following zstack
            start_time_index = last_index_start
        else:
            #this shouldn't happen
            print('odd scenario. not in same z-stack and not between z-stacks')
            
        #end time
        first_index_end = np.where(first_timestamps_s < end_time)[0][-1]
        last_index_end = np.where(last_timestamps_s > end_time)[0][0]
        if first_index_end == last_index_end:
            end_time_index = first_index_end
        elif last_timestamps_s[first_index_end] < end_time < first_timestamps_s[last_index_end]:
            #ending index choose the zstack before (miss the bit between, but I'm removing that data anyway)
            #changin this to last index because it's been ending too early
            end_time_index = last_index_end
        else:
            #this shouldn't happen
            print('odd scenario. not in same z-stack and not between z-stacks')

        both = (start_time_index, end_time_index)
        forty_switch_set_t.append(both)
    twenty_switch_set_t = np.array(twenty_switch_set_t)
    forty_switch_set_t = np.array(forty_switch_set_t)
    return twenty_switch_set_t, forty_switch_set_t

def get_times_switch_blocks (dataset_path, exp_length1 = 20, exp_length2 = 40):
    """returns array of arrays of times in s that each block 
    starts and ends seperate arrays returned for 20 and 40 (or specified expt times)
    i.e. 20s_times = [[30.9 400.2][600.7  987.6]]  [[start1 stop 1] [start 2 stop 2]] """
    
    
    light_peaks_path = os.path.join(dataset_path, 'light_peaks.h5')
    opened_peaks = open_light_peaks(light_peaks_path)
    if opened_peaks is not None:
        light_peaks = opened_peaks/1000
        print('found light in h5 file')
    else:
        light_peaks = get_light_peaks(dataset_path)/1000
    twenty, forty = get_switch_start_stop_indices(dataset_path, exp_length1, exp_length2)
    
    light_peaks_twenty_times = []
    for set_index in range(len(twenty)):
        t = (light_peaks[twenty[set_index][0]], light_peaks[twenty[set_index][1]])
        light_peaks_twenty_times.append(t)

    light_peaks_forty_times = []
    for set_index in range(len(forty)):
        t = (light_peaks[forty[set_index][0]], light_peaks[forty[set_index][1]])
        light_peaks_forty_times.append(t)

    light_peaks_twenty_times = np.array(light_peaks_twenty_times)
    light_peaks_forty_times = np.array(light_peaks_forty_times)
    
    return light_peaks_twenty_times, light_peaks_forty_times


##support functions
def get_switch_start_stop_indices(dataset_path, exp_length1 = 20, exp_length2 = 40):
    """returns an array of tuples of start and stop indices for starts and stops of 20s or 40s. 
    20 and 40 are returned in seperate arrays.
    inclusive (start = first index and stop = last index)"""
    switch_points = find_switch_points(dataset_path)
    light_peaks_path = os.path.join(dataset_path, 'light_peaks.h5')
    opened_peaks = open_light_peaks(light_peaks_path)
    if opened_peaks is not None:
        light_peaks = opened_peaks/1000
    else:
        light_peaks = get_light_peaks(dataset_path)/1000
    
    light_times = light_peaks[1:]- light_peaks[0:-1]
    twenty = []
    forty = []
    for i in range(len(switch_points)):
        switch_index = switch_points[i] 
        print(switch_index)
        print(light_times[switch_index])
        if i == 0:
            if exp_length1 - 5 < light_times[switch_index] < exp_length1 + 5:
                t = (0, switch_index + 1) #the + 1 helps it end and start at the same place
                twenty.append(t)
            elif exp_length2 - 5 < light_times[switch_index] < exp_length2 + 5:
                t = (0, switch_index + 1)
                forty.append(t)
        else:
            previous_index = switch_points[i - 1] + 1 
            if exp_length1 - 5 < light_times[switch_index] < exp_length1 + 5:
                t = (previous_index, switch_index + 1)
                twenty.append(t)
            elif exp_length2 - 5 < light_times[switch_index] < exp_length2 + 5:
                t = (previous_index, switch_index + 1)
                forty.append(t)
    twenty = np.array(twenty)
    forty = np.array(forty)
    return twenty, forty


def find_switch_points(dataset_path, difference=15):
    """takes dataset path and imports light peaks and returns the times there is a switch
    args:
    dataset_path = path to fly folder that has voltage file
    difference = value that it will sort by to see if there is a switch point. 
    The difference between two intervals should be greater than this number (i.e. 40-20 = 20 >15)
    returns:
    indices of the last trial before switch"""
    
    #get light peaks
    light_peaks_path = os.path.join(dataset_path, 'light_peaks.h5')
    opened_peaks = open_light_peaks(light_peaks_path)
    print(opened_peaks)
    if opened_peaks is not None:
        light_peaks = opened_peaks/1000
    else:
        light_peaks = get_light_peaks(dataset_path)/1000
    
    #find times between light flashes
    light_times = light_peaks[1:]- light_peaks[0:-1] 
    #check that light peaks is single light peaks 
    if len(np.where(light_times < difference)[0]):
        #light_peaks is taking more than one datapoint per peak
        raise Exception(f'WARNING: these are not single peaks check indices {np.where(light_times<15)[0]}')
    
    #find switch points
    light_times_diff = np.rint(abs(light_times[1:] - light_times[0:-1]))
    switch_ind = np.where(light_times_diff > 15)[0] 
    #switch_ind = np.insert(switch_ind, 0,light_times_diff[0]) #This will add 0 but I don't need it
     
#     ##switch times in s
#     switch_times_s = light_peaks[switch_ind]
    
#     #block interval values
#     #skip 0 because it is dark and then subtract 1 to make sure its in the block 
#     #(the end point is the last point anyway so it should be fine without the -1)
#     ind_to_get_ints = switch_ind[1:] - 1 
#     interval_sets = light_times[ind_to_get_ints]
#     interval_sets_int = [int(i) for i in interval_sets]
    
    return switch_ind