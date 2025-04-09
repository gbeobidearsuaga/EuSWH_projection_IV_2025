# Detection of Heat Waves
"""
Created on Mon Apr 20 14:58:34 2020

@author: Goratz Beobide-Arsuaga (goratz.beobide.arsuaga@uni-hamburg.de)

Detecting heat waves FOR EACH GRID-POINT by exceeding a threshold for at least X consecutive days. 
Data: xarray, with (time,lat,lon) dimensions
Threshold Input: same dimensions as data
C_days: number of consecutive days data must exceed threshold
"""

# --------------------------------------------------------------------------------------------------------------
# ----------------- Fixed threshold for each JJA day (one fixed value for each JJA day) ------------------------
def gb_hwdetect(data,threshold_input,c_days):
    import sys
    from copy import deepcopy
    import numpy as np
    import xarray as xr
    
    years = np.unique(data.time.dt.year).shape[0]
    len_year = int(data.time.shape[0]/years)
    len_year_check = data.time.shape[0]/years
    hw_count_withtime = deepcopy(data)
    hw_count_withtime[:] = 0
    
    #check if input data and threshold dimensions agree
    for d in range(len(data.dims)):
        if data.shape[d] != threshold_input.shape[d]:
            sys.exit('input data and threshold dimensions do not coincide')
    
    #check if the size of years are homogeneous, bisiesto?
    if len_year!=len_year_check:
        sys.exit('Years not homogeneous!')
    
    #flatten lon/lat dims
    joker = data.values.reshape(-1,data.lat.shape[0]*data.lon.shape[0])
    
    #treat differently if input threshold is xarray or numpy
    if type(threshold_input) == xr.core.dataarray.DataArray:
        joker_threshold = threshold_input.values.reshape(-1,threshold_input.shape[1]*threshold_input.shape[2])
    if type(threshold_input)  == np.ndarray:
        joker_threshold = threshold_input.reshape(-1,threshold_input.shape[1]*threshold_input.shape[2])
    if (type(threshold_input) != xr.core.dataarray.DataArray) & (type(threshold_input)  != np.ndarray):
        sys.exit('Threshold input is not xarray nor numpy!')
    
    #create a year/days dimensions
    joker = joker.reshape(years,len_year,data.lat.shape[0]*data.lon.shape[0])
    joker_threshold = joker_threshold.reshape(years,len_year,threshold_input.shape[1]*threshold_input.shape[2])
    
    #create hw_detect array
    hw_count = deepcopy(joker)
    hw_count[:,:,:] = 0 
    
    for x in range(0,joker.shape[2]):
        if ~np.isnan(joker[0,0,x]):
            cc = -1
            hw_duration = 0 
            for tt in range(years): 
                hw_duration = 0 
                for t in range(0,len_year): 
    
                    if joker[tt,t,x] >= joker_threshold[tt,t,x]:
                        hw_duration = hw_duration + 1
        
                        #for all the values besides the last value of timeseries
                        if (t != len_year-1): 
                            if (joker[tt,t+1,x] < joker_threshold[tt,t+1,x]): 
                                if (hw_duration >= c_days): 
                                    end = t+1
                                    start = end - hw_duration
                                    hw_count[tt,start:end,x] = 1
                                hw_duration = 0 #if next value not exceeding threshold, set hw_duration to zero
        
                        #for the last value of timeseries  
                        elif (t == len_year-1) & (hw_duration >= c_days): 
                            end = t+1
                            start = end - hw_duration
                            hw_count[tt,start:end,x] = 1
                            
    hw_count_withtime[:,:,:] = hw_count.reshape(data.shape[0],data.lat.shape[0],data.lon.shape[0])
    return hw_count_withtime