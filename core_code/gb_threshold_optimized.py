# -*- coding: utf-8 -*-
"""
Created on Thu May 21 15:27:00 2020

@author: Goratz Beobide 
"""

#-------------------------------------------------------------------------------------------------
#------------------------ Threhold fixed in years but moving in days -----------------------------
#-------------------------------------------------------------------------------------------------

#Compute a threshold for each day of the year, on a "percentile_window" range. 
#We have DIFFERENT thresholds for each day of a year, based on a specified window, but we have same values for the days in different years (i.e. 1st of January of all years)

def gb_threshold_fixed_day(data,percentile,percentile_window,position):
    """
    data: xarray 
    percentile: the reference for extreme, ie. 90
    percentile window: the size of the window for the percentile, ie. 15
    position: how to fill missing values due to running window. 'centered' or 'backend'
    """
    import numpy as np
    import sys
    
    years = np.unique(data.time.dt.year).shape[0]
    len_year = int(data.time.shape[0]/years)
    len_year_check = data.time.shape[0]/years
    window_number = len_year-percentile_window+1 #number of windows

    if len_year!=len_year_check:
        sys.exit('Years not homogeneous!')
        
    #flatten lon/lat dims
    joker = data.values.reshape(-1,data.lat.shape[0]*data.lon.shape[0])
    
    #create a year/days dimensions
    joker = joker.reshape(years,len_year,data.lat.shape[0]*data.lon.shape[0])

    #Compute the threshold
    threshold = np.zeros((window_number,joker.shape[2]))
    for w in range(window_number):
        joker2 = np.roll(joker,-w,axis=1)
        threshold[w,:] = np.percentile(joker2[:,:percentile_window].reshape(-1,joker2.shape[2]),percentile,axis=0)
        
    
    #Fill missing values due to running window
    threshold_fill = np.zeros((len_year,joker.shape[2])) #add missing values    
    #position = 'centered' # centered or backend
    if position == 'centered':
        miss = int((percentile_window-1)/2) #number of missing points  
        threshold_fill[:miss] = threshold[0]
        threshold_fill[-miss:] = threshold[-1]
        threshold_fill[miss:-miss] = threshold
    elif position == 'backend':
        miss = int(percentile_window-1)    
        threshold_fill[:miss] = threshold[0]
        threshold_fill[miss:] = threshold
    else:
        sys.exit('Position not well defined!')

    
    #Extend threshold to whole set of initial years (ONLY for fix_day) and return to original lat/lon dimensions
    threshold_complete = np.repeat(threshold_fill[np.newaxis,:],years,axis=0)
    threshold_complete = threshold_complete.reshape(data.shape[0],data.lat.shape[0],data.lon.shape[0])
    
     
    return threshold_complete