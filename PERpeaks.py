
## new scipy peaks that does just PER-peaks

import numpy as np
from matplotlib import pyplot as plt
import os
os.listdir(os.getcwd())

import csv as csv
import json as json
import pickle as pickle

import scipy as scipy
from scipy.signal import find_peaks
import h5py

def main():
    date = '20230130'
    date_code = 'b-0130-120'  #for fly names (b for bruker 4 code date and fly #)
    Pathstart = '/Users/ashsm/OneDrive/Documents/Stanford/Bruker behavior/' + str(date) + '/results/'
    SavePath = '/Users/ashsm/OneDrive/Documents/Stanford/Bruker behavior/' + str(date) + '/scipy/'
    make_dir(SavePath)
    #C:\Users\ashsm\OneDrive\Documents\Stanford\Bruker behavior\20230130\results

    list_map = {
        #'none': ['Results_video_2_python.csv'] # the dictionary key tells you what kind of video it is
        20: ["Results_video_fly1-20s_frames_python.csv" , 'Results_video_fly3-20s_frames_python.csv'],
        40: ['Results_video_fly1-40s_frames_python.csv', 'Results_video_fly2-40s_frames_python.csv']
    }

    #current_file = "Results_video_fly1-20s_frames_python.csv"

    files = os.listdir(Pathstart)

    #get filenames
    file_name_list = []
    for i in range(len(files)):
        if '.csv' in files[i]: 
            csv_file = []
            csv_file = files[i]
            file_name_list.append(csv_file)
            print (files[i])
        else:
            print('no')
    print('file name list', file_name_list)


    video_framerate = 200 #f/s
    interval_ms_list, ask = get_intervals_and_asks(list_map, file_name_list)

    

    ##I could alternatively open files when I need them rather than storing them all in memory...
    data_all = []
    light_data = []
    for single_file in file_name_list:
        with open(os.path.join(Pathstart, single_file), 'r') as rawfile:  #'rb' in python2
        # reader = csv.reader(psth, delimiter="\t")
            reader = csv.reader(rawfile)
            
            if 'Results' in single_file:
                data_single = list(reader)
                data_all.append(data_single)
            elif 'Voltage' in single_file:  #will need to sort out the fly order later
                data_single = []
                for i, row in enumerate(reader):
                    if i % data_reducer == 0:  #this will downsample the data by taking every 100, i % 100 means will divide i by 100 and take the ones that have no remainder
                        data_single.append(row)
                light_data.append(data_single)
    #print('intdata', intdata)
    print(len(data_all))
    print(len(file_name_list))


    ## there is only one fly per bruker vid so I am removing the info to designate fly numbers
    fly_number_list = []
    for i in range(len(data_all)):
        fly_number = str(date_code) + '-' + str(i+1)
        fly_number_list.append(fly_number)
    print(fly_number_list)






    #________RUN CODE_____________
    for data_index in range(len(data_all)):
        data = data_all[data_index]

        framerate = video_framerate
        interval_ms = interval_ms_list[data_index]

        #get video name
        video_file = file_name_list[data_index]
        video = str(video_file).strip('Results_').strip('.csv')
        print(f"----CURRENTLY RUNNING ----> {video_file}")

        PER_peaks, PER_peak_properties, PER_columns = get_peaks(data)

        PER_peaks_sec = np.array(PER_peaks[0]) / video_framerate  #need to do [0] because designed for more than one fly

        #onsets doesn't work for this data use left bases from peak properties
    #     PER_onsets_matrix_sec = get_onsets_matrix(PER_peaks_sec, data, PER_columns, identifier = 'PER')
    #     light_onsets_matrix_sec = get_onsets_matrix(light_peaks_sec, light_data[data_index], light_columns, identifier = 'light')
        
        PER_onset_indices = PER_peak_properties['left_bases']

        #get raw
        mean_indices = get_mean_indices(data)
        mean_titles = get_mean_titles(data)
        for mean_index in range(len(mean_indices)):
            single_column = get_means(data, mean_indices[mean_index])
            if is_column_light(mean_titles, 0, mean_index) or 'diode' in mean_titles[0][0]:
                print('light')
                raw_light = single_column
                add_to_h5(h5_file, 'raw light', raw_light)

            else:
                raw_PER = single_column



        ##if light in csv file then do these
        #light_peaks, light_peak_properties, light_columns = get_peaks(light_data[data_index])
        #light_peaks_sec = np.array(light_peaks[0]) / video_framerate
        #light_onset_indices = light_peak_properties['left_bases']
        print(f"video name = {video} is done")
        print(np.shape(PER_peaks))


        ##add to h5py file
        h5_file = os.path.join(SavePath, str(video) + '_peaks.h5')
        #f = h5py.File(h5_file, "w")
        #with h5py.File(h5_file, 'a') as f:
        add_to_h5(h5_file, 'PER peaks', PER_peaks)
        add_to_h5(h5_file, 'PER peaks (s)', PER_peaks_sec)
        add_to_h5(h5_file, 'PER onsets', PER_onset_indices)
        add_to_h5(h5_file, 'raw PER', raw_PER)
        print(f'video {video} is saved')
        
        

        print(f"============ Video name = {video} is saved!   ============")









##______________FUNCTIONS__________________##
##not all of these functions are used. Need to clear out unused ones and clean up
def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def add_to_h5(path, key, value):
    """adds new key value to h5 file and checks if it already exists. Does overwrite"""
    with h5py.File(path, 'a') as f:
        if key not in f.keys():
            f[key] = value
        else:
            del f[key]
            f[key] = value


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



#to see if the column is a mean
def is_column_mean (data, row, column):
    """return true if cell contains 'mean'"""
    return "Mean" in data[row][column] or "diode" in data[row][column]  #diode added for bruker

#collecting all of the values in a column
def get_means(data, column_number):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    mean_list = []
    """gets column for (data, column_number) and eliminates the header (row 0) and puts it into a np.array"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        mean_list.append(row[column_number])
    means = np.asarray(mean_list[1:], dtype=np.float64) #changes the list into a numpy array. [1:] means take the second number to the end 
    #(to get rid of the title). dtype changes from strings to np integers
    return means

def get_header(data, column_number):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    title_list = []
    """gets header (row 0) for data set for specified column (data, column number)"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        title_list.append(row[column_number])
    titles = np.array(title_list[:1]) #changes the list into a numpy array. [:1] means take the first row
    return titles

def get_video_name(data, column):  #this will pull from whatever you call the variable that you have gotten your csv data from and specified column 
    video_name = []
    """gets video name (row 2) for data set for specified column (data, column number)--specify column 2 (1)"""
    for row in data: #row is the variable with the row number in it if use range(len(data)) it gives a list of the row if just use data
        #print row
        video_name.append(row[column])
    video = np.array(video_name[1:2]) #changes the list into a numpy array. [1:2] means take the second row
    return video


# find the mean(light) columns
##bruker addition
def is_column_light (data, row, column):
    """return true if the column contains 'light' or 'Light'"""
    return "Light" in data[row][column] or "light" in data[row][column] or " diode" in data[row][column]


##specify which columns are PER by checking the column numbers in mean_titles
def is_column_PER (data, row, column):
    """return true if the column contains 'PER)' or 'per)' or 'Per)'"""
    return "PER)" in data[row][column] or "per)" in data[row][column] or 'Per)' in data[row][column]
    #in the fiji files the title is Mean(PER) so the ) lets it distinguish between PER and PER#


def make_bins (time_range, binsize):
    """to make bins based on desired time range and binsize--use ms"""
    ms_binlength = np.asarray(range(int(time_range/binsize) + 1)) * binsize
    return ms_binlength



def make_title (date, video, fly_id, interval_s):
    title = str(date) + str(video).strip('[]') + str(fly_id) + '-flyID_' + str(interval_s) + '_int'
    return title

def get_PER_smooth_out (PER_index, smoothed_intensity_decreases):
    """new function to just get PER smooth out--not sure why I have to do all these manipulations"""
    #use decreases because PER is out when intensity drops
    PER_index = np.asarray(PER_index)
    PER_index_int = int(PER_index) ##to convert to integer so ends up with only one list and not a list of zeros
    PER_smooth_out = np.nonzero(smoothed_intensity_decreases[:,PER_index_int])  #light_indices specifies light column
    PER_smooth_out = PER_smooth_out[0]
    PER_smooth_out = np.asarray(PER_smooth_out)
    return PER_smooth_out

def get_single_PER_smooth(PER_index, smoothed_intensity_decreases):
    """adjusts PER smooth so that each PER is hopefully just a single timepoint. 
    Attempts to remove continued responses after initial"""
    PER_smooth_out = get_PER_smooth_out(PER_index, smoothed_intensity_decreases)
    single_PER_smooth = []
    for per in PER_smooth_out:
        #if the single_PER smooth list is empty or the previous item in the list is 3 less than than the current
        if not single_PER_smooth or per > single_PER_smooth[-1] + 3:
            single_PER_smooth.append(per)
    return single_PER_smooth
def get_mean_indices(data):
	"""get indices where there are means from data from one fly (previous code this was called mean_column"""
	mean_indices = []
	for row in range(len(data)):
		for column in range(len(data[row])):
			if is_column_mean(data, row, column):
				mean_indices.append(column) #store column index
	return mean_indices

def make_means_matrix(data):
	"""data should be the raw data for one fly, returns matrix of just the means data"""
	#1. get mean column indices
	mean_indices = get_mean_indices(data)

	#2. make the means matrix
	columns = []
	for item in mean_indices:
		columns.append(get_means(data, item))
	means_matrix = np.vstack(columns).T # converts the list of arrays into a matrix ".T" makes it report tall   
	return means_matrix

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
    
def get_light_index(data):
    """ take fly data and return the array with column number(s) for "light" or "Light"""
    mean_titles = get_mean_titles

    light_indices = []
    for row in range(len(mean_titles)):
        for column in range(len(mean_titles[row])):
            if is_column_light(mean_titles, row, column):
                light_indices.append(column)
    light_indices = np.array(light_indices)
    return light_indices

def get_peaks(data):
    """	data = one flies worth of raw data, 
    returns list of list of peaks for light and PER where light and PER have different scipy requirements
    may need to change some parameters in scipy find peaks if there is an issue finding them"""

    #1. get mean column indices and mean titles
    mean_indices = get_mean_indices(data)
    mean_titles = get_mean_titles(data)

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
            
        else:
            print('PER')
            peaks, properties = scipy.signal.find_peaks(squeeze_column*-1, prominence = 3, distance = 15) 
            columns.append(single_column)
            #distance is req frames between peaks
        all_peaks.append(peaks)
    return all_peaks, properties, columns

def get_smoothed_intensity_changes(data):
    """returns decreses in intensity and increases"""
    smoothed_means_matrix = get_smoothed_means_matrix(data)
    
    #to just see if previous value greater than next value of smoothened array--if the intensity drops
    smoothed_intensity_decreases = []
    smoothed_intensity_decreases = smoothed_means_matrix[:-1]>(smoothed_means_matrix[1:] + smoothed_threshold)
    smoothed_intensity_decreases = smoothed_intensity_decreases.T  #want to stack the other way
    
    #to just see if previous value smaller than next value of smoothened array--if the intensity increases
    smoothed_intensity_increases = []
    smoothed_intensity_increases = smoothed_means_matrix[:-1]<(smoothed_means_matrix[1:] + smoothed_threshold)
    smoothed_intensity_increases = smoothed_intensity_increases.T
    
    return smoothed_intensity_decreases, smoothed_intensity_increases

def get_smoothed_means_matrix(data):
    """inputs data and returns smoothed_means_matrix, smoothed_intensity_decreases, smooothed_intensity_increases"""
    #call each column to perform the vectorized smoothing average over 3 frames to see if it changes intensity
    ##Essentially take windowsize number of columns that are off by 1 until get to windowsize (in this case=3)
    ##[begin:end:stride] end is exclusive so if you want to include item #n write n+1. -1 is second to last
    ###NOTE: this will not give a value for the last 2 items (will shorten the array by 2) 
    
    means_matrix = make_means_matrix(data)

    smoothed_means_matrix = []
    smoothed_means_matrix = means_matrix[:-2]/3 + means_matrix[1:-1]/3 + means_matrix[2:]/3
    
    return smoothed_means_matrix


def get_smoothed_decrease_index(data):
    """return indices where intensity decreases from smoothed matrix"""
    smoothed_intensity_decreases, smooothed_intensity_increases = get_smoothed_intensity_changes(data)
    smoothed_decrease_index = []
    for column in range(len(smoothed_intensity_decreases)):
        true_indices = np.where(smoothed_intensity_decreases[column])
        smoothed_decrease_index.append(np.squeeze(true_indices))
    return smoothed_decrease_index
    
def get_intensity_increase_index(data, threshold = 10):
    """this is equivalent to up_50_index in previous code.
    Returns: differences between frames that are > 10 """
    
    means_matrix = make_means_matrix(data)
    intensity_up = means_matrix[1:]-means_matrix[:-1]>=threshold
    
    intensity_up = intensity_up.T
    up_index = []
    for column in range(len(intensity_up)):
        true_indices = np.where(intensity_up[column])
        up_index.append(np.squeeze(true_indices))
    return up_index

def get_smoothed_intensity_decrease_index(data, smoothed_threshold = 1):
    """this is equivalent to smoothed_decrease_index in previous code.
    Returns: differences between frames taht are > 10 """
    
    means_matrix = make_means_matrix(data)
    intensity_up = means_matrix[1:]-means_matrix[:-1]>=10
    
    intensity_up = intensity_up.T
    up_index = []
    for column in range(len(intensity_up)):
        true_indices = np.where(intensity_up[column])
        up_index.append(np.squeeze(true_indices))

    return up_index

def get_onsets_matrix(all_peaks, data, columns, light_threshold = 50, PER_threshold = 50, identifier = 'all'):
    #possibly swap out so all peaks isn't needed? or run all_peaks seperate if needed for other things
    """find onset of peaks from scipy peaks and intensity changes
    #onset is found by looking at the frames of peaks and looking for the smoothed_intensity change before that
    #for PER looking for a decrease, for light looking for an increase
    #each per or light can be accessed by means_matrix[:, index of per (column)]
    #I want to look at the peaks values of each column and compare them to the intensity changes of each column (depending on if it is light or not)
    #light index is light_indices
    threshold is max # of frames away from peak to look for onset
    OUTPUT is boolean matrix, if need the other matrix later then rewrite return to be all_onsets_matrix as well"""
    
    if identifier == 'all':
        light_indices = get_light_index(data)
        
    up_index = get_intensity_increase_index(data)
    #all_peaks = get_peaks(data) #for now I'm leaving all_peaks in so it doesn't have to calculate them again
    smoothed_decrease_index = get_smoothed_decrease_index(data)
    
    
    all_onsets_matrix = []
    for mean_item_index in range(len(all_peaks)): #mean item index is light or PERs
        onsets = []
        onset = [] 
        #if identifier == 'all' or identifier == 'PER': #the index is for a PER
        if identifier == 'PER' or (identifier == 'all' and mean_item_index != light_indices):
            for i in range(len(all_peaks[mean_item_index])):
                possible_onset = []
                new_possible_onset = []
                if smoothed_decrease_index[mean_item_index].size > 1: #if it is not empty or one element
                    for j in range((smoothed_decrease_index[mean_item_index].size)):
                        if smoothed_decrease_index[mean_item_index][j] <                         all_peaks[mean_item_index][i] and all_peaks[mean_item_index][i] -                         smoothed_decrease_index[mean_item_index][j] < PER_threshold: 
                            #if the value is less than the peak and the onset isn't far from peak (here 50 frames)
                            possible_onset.append(smoothed_decrease_index[mean_item_index][j]) #make a list of possible onsets 
                        else:
                            possible_onset.append(0) #hopefully this will fix if the onsets and peaks don't match    
                    if i == 0: #if we are on the first element in peaks_PER
                        if possible_onset: #checks to make sure there is something in possible_onset
                            onset = int(np.median(possible_onset)) #needs to be int because it is an index
                    if i > 0: #if it is not the first element
                        #remove the possible onsets that are before the previous peak then take the first one
                        for onset_index in possible_onset:
                            if onset_index > all_peaks[mean_item_index][i-1]:  
                                #I need to fix this in case it is not >. I think skip otherwise?
                                new_possible_onset.append(onset_index)
                                #onset = new_possible_onset[0]  
                                #might be better if this doesn't have to collect the first one everytime, 
                                # but it should work fine and eliminates the issue if the if statement is not true
                                onset = int(np.median(new_possible_onset)) #needs to be int because it is an index
                    #to prevent appending empty lists
                    if onset:  #this fails if onset is an empty list and will not append anything
                        onsets.append(onset)
        elif identifier == 'light' or mean_item_index == light_indices: #if the index corresponds to light index then use intensity up 50
            print('light version')
            for i in range(len(all_peaks[mean_item_index])):
                possible_onset = []
                new_possible_onset = []
                if up_index[mean_item_index].size > 1: #if it exists and has more than one element
                    for j in range(len(up_index[mean_item_index])):
                        if up_index[mean_item_index][j] < all_peaks[mean_item_index][i] and               all_peaks[mean_item_index][i] - up_index[mean_item_index][j] < light_threshold: 
                            #if the value is less than the peak and the onset isn't far from peak (here 50 frames)
                            possible_onset.append(up_index[mean_item_index][j]) #make a list of possible onsets
                        else:
                            possible_onset.append(0) #hopefully this will fix if the onsets and peaks don't match
                    if i == 0: #if we are on the first element in peaks_PER
                        if possible_onset: #this will check if possible_onset is an empty list, if it is it will fail
                            onset = possible_onset[0]  
                            #then the onset is the first in the list... this could fail sometimes, but hopefully with frame limit it won't
                    if i > 0: #if it is not the first element
                        #remove the possible onsets that are before the previous peak then take the first one
                        for onset_index in possible_onset:
                            if onset_index > all_peaks[mean_item_index][i-1]:
                                new_possible_onset.append(onset_index)
                                onset = new_possible_onset[0]
                    #to prevent appending empty lists
                    if onset:  #this fails if onset is an empty list and will not append anything
                        onsets.append(onset)  #these are light but will add PER below
        
        all_onsets_matrix.append(onsets)
    
        #convert all_onsets into a boolean
        onsets_boolean = []
        for index in range(len(all_onsets_matrix)):
            boolean_single = []
            for i in range(len(columns[0])): #because it has all of the elements not just the ones with peaks
                if i in all_onsets_matrix[index]: #look through each index and see if it is in the onsets list
                    boolean_single.append(True) #if it is replace with true
                else:
                    boolean_single.append(False)
            onsets_boolean.append(boolean_single)
        bool_onsets_matrix = np.vstack(onsets_boolean).T
        
    return bool_onsets_matrix

def get_light_on_indices(bool_onsets_matrix, data):
    """this will return light_on which used to be light_up_50 and it is the indices where the light onsets"""
    light_indices = get_light_index(data)
    light_on_indices = bool_onsets_matrix[:,light_indices]
    light_on = np.squeeze(np.where(light_on_indices))
    return light_on
    

    
    
def get_PER_number(value):  # Don't actually include =data[row][column], but that's how you'd call this.
    """input is value=data[row][column]
    output is the value of the PER. For example if it finds PER4 it will return 4, if it finds PER it will return 0"""
    if "PER" in value:  # If this should handle "per", does it mak sense if this is value.lower()
        per_start = value.find("PER")
        paren_start = value.find(")", per_start)
        if paren_start == 3:
            return 0
        return int(value[per_start+3:paren_start])
    if "per)" in value or "Per)" in value:
        return 0
    else:
        return None


#get indices of different PERs
def get_PER_list_fly_list(data, fly_number_list):
    """returns the PER_list and the fly_id order"""
    mean_titles = get_mean_titles(data)
#how do I figure out if it is the right column...
    for item_index in range(len(mean_titles)):
        PER_list = []
        fly_id_list = []
        value = get_PER_number(mean_titles[item_index])
        if value is not None:  #if it is not none then it is a value...
            PER_list.append(item_index) #PER list should be index of the column
            fly_id = fly_number_list[value]  # the value indicates the index for the flies because it corresponds to the PER number
            ##why does fly_number_list have a data index? ...if this doesn't work it is because it used to be fly_number_list[data_index][2]
            # might get messed up if there are two experiments on the same day??
            
            # POTENTIAL ERROR HERE! make sure this works for two experiments on the same day##
            
            fly_id_list.append(fly_id)
    print('POTENTIAL ERROR HERE! make sure this works for two experiments on the same day')
    return PER_list, fly_id_list     


 



if __name__=='__main__':
  main()

