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
        print("Caution: this does not contain 'Voltage', make sure it's the right file")
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


def find_fly_string(string):
    """things after fly will be returned as string"""
    post_fly_string = string.split("fly",1)[1]
    return post_fly_string

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
    
    return "Mean" in data[row][column] or "diode" in data[row][column] or " Input 0" in data[row][column] 

def get_header(data, column_number):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    title_list = []
    """gets header (row 0) for data set for specified column (data, column number)"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        title_list.append(row[column_number])
    titles = np.array(title_list[:1]) #changes the list into a numpy array. [:1] means take the first row
    return titles

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
	return data[row][column] in str_list

def is_column_light(data, row, column):
	return is_column_in_list(data, row, column, ("Light", "light", "diode", "Mean(Light)", " Input 0"))




##
def get_peaks(data, h5file,  override = False,):
    """ uses scipy peaks to find peak points of data 
    finds negative peaks for PER and positive peaks for light. 
    Will also add the peaks to the h5 file of the fly
    args: 
        data = raw data imported that contains a header with "mean", "diode", "input 0"
        h5file = path to h5 file data to save peaks data
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

    if len(mean_indices) < 1:
        if override == True:
            squeeze_column = np.squeeze(data)
            peaks, properties = scipy.signal.find_peaks(squeeze_column*-1, prominence = 3, distance = 15) 
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
        if is_column_light(mean_titles, 0, mean_index) or 'diode' in mean_titles[0][0]:
            print('light')
            #peaks, _ = scipy.signal.find_peaks(squeeze_column, prominence = .5)
            columns.append(single_column)
            ##modification for noisy diode data
            light_median = np.median(single_column, axis = 0)
            early_light_max = max(single_column[0:2000])
            #peaks, _ = scipy.signal.find_peaks(squeeze_column, height = light_median[0], prominence = .3, distance = 10)
            peaks, properties = scipy.signal.find_peaks(squeeze_column, height = early_light_max +.001, prominence = .1, distance = 10)
            add_to_h5(h5file, 'light peaks', peaks)
            
        else:
            print('PER')
            peaks, properties = scipy.signal.find_peaks(squeeze_column*-1, prominence = 3, distance = 15) 
            columns.append(single_column)
            add_to_h5(h5file, 'PER peaks', peaks)
            #distance is req frames between peaks
        all_peaks.append(peaks)
    return all_peaks, properties, columns


