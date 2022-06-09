import os
import subprocess
import sys

#this will pull the first jpeg from a folder and copy it to the destination folder if it finds files in the fly folder under analysis for each date
#it will also rename the file with the date and fly number
# this will continue to collect more files if it is run again that may or may not be the same file. 

dates = ['20210716', '20210714', '20210709', '20210702', '20210607']
         

destination = '/oak/stanford/groups/trc/data/Ashley2/bruker videos/for_rois'



def main():
  make_dirs(destination)
  
  for date in dates: 
    data_path = '/oak/stanford/groups/trc/data/Ashley2/bruker videos/' + str(date) +'/'   #should end in /
    #look for analysis folder
    folders = os.listdir(data_path)
    if 'analysis' in folders:
        analysis_path = os.path.join(data_path, 'analysis')
        for fly in os.listdir(analysis_path):
            #open folder and get first frame then save it in roi folder with a new name
            fly_path = os.path.join(analysis_path, fly)
            if len(os.listdir(fly_path)) > 0: 
                file = os.listdir(fly_path)[0]
                file_path = os.path.join(fly_path, file)
                new_filename = str(date) + str(fly) + str(file)
                print(new_filename)
                dst_path = os.path.join(destination, new_filename)
                shutil.copy(file_path, dst_path)
                
                
    
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
