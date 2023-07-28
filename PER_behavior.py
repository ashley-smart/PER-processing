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


# get paths
date = '20230407'
fly_id_date_code = 'b-0407'

Path = 'G:/bruker vid 2023/20230407/results/'  #path to results files from read ROIs or DLC
Savepath = Path

#####  import data  ###
#(allow for bruker light data or video light data)
#(also allow for video PER data and DLC per data)

#check for voltage file -> trigger voltage reading of light
#store the data in an h5py file with the fly # as the key 
# so I don't have to worry about aligning the PER and the light in the same order
#





#set framerate







#set interval time






#set fly numbers




#get peaks for light and PER








#smooth PER peaks 






#find onset of PER peaks



#find indiv






#