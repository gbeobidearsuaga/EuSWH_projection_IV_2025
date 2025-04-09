#!/usr/bin/env python
# coding: utf-8

# In[1]:


f_path = '/home/u/u241308/script_python/gb_functions'
import sys
sys.path.insert(1, f_path)
import gb_hwdetect_optimized as gb_hw

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import xarray as xr
import copy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from math import sin, cos, sqrt, atan2, radians


# In[2]:


#reference time
ref_min = 1985
ref_max = 2014

# Consecutive days for heatwave detection
c_days = 6

# Threshold percentile
percentile = 90 #90

#Definition type: daily moving threshold (mov_day) or JA moving threshold (mov_JA)
def_type = 'fix_day' #'mov_JA'

#Define run
run_type = ['HIST','ssp119','ssp126','ssp245','ssp370','ssp585']
#run_type = ['ssp119','ssp370']

run = 5


# In[3]:


def run_hw_detect(ens):   
    ens_total = 30 + ens #starts in ensemble 30 for threshold, but temperatures are in different format starting with ensemble 1
    #import data
    path = '/work/uo1075/u241308/data_python_PostDoc/MPI_GE_cmip6/t2max/'
    file = 'nGE_Tmax_'+ run_type[run] +'_dm_ens_31-50_land_europe_ens_mean_anomaly_detrend.nc'
    
    with xr.open_dataset(path+file) as data1:
        data1 = data1.tasmax
    
        #Select ensemble members
        data1 = data1[:,ens,:,:]
        
        #Get rid off 29th of februarys
        data1 = data1.sel(time=~((data1.time.dt.month == 2) & (data1.time.dt.day == 29)))
        
    #load threshold
    path = '/work/uo1075/u241308/data_python/HW_extension/GE_cmip6/anomaly/threshold/'  
    file = 'threshold_%s'%percentile+ '_' + def_type +'_GE_ref_%i-'%ref_min + '%i_'%ref_max + 'ensemble_%i_anomaly_detrend.nc'%ens_total
    
    with xr.open_dataset(path+file) as threshold:
        threshold = threshold.tasmax
        
        #select one year (all years are the same in fix_day)
        threshold = threshold[(threshold.time.dt.year==threshold.time.dt.year.min())].values
        
    #expand threhsold to dimensions of data1
    year_number = np.unique(data1.time.dt.year).shape[0]
    out_data = copy.deepcopy(data1)
    out_data[:,:,:] = np.tile(threshold,(year_number,1,1))
        
    #detect hws
    heat_wave_day_withtime1 = gb_hw.gb_hwdetect(data1,out_data,c_days)
    out_data[:,:,:] = heat_wave_day_withtime1
            
    return out_data


# In[4]:


#SELECT ensemble members to run the code
ens_0 = 0
ens_n = 20


# In[ ]:


for ens in range(ens_0,ens_n):
    ens_total = ens + 30
    hw_detect = run_hw_detect(ens)
    
   #save data
    path = '/work/uo1075/u241308/data_python/HW_extension/GE_cmip6/anomaly/hw_detect/'+run_type[run]+'/'
    file = 'hw_detect_%id'%c_days +'_%s'%percentile+ '_' + def_type + '_GE_'+ run_type[run] +'_ref_%i'%ref_min + '-%i'%ref_max + '_ensemble_%i_anomaly_detrend.nc'%ens_total    
    hw_detect.to_netcdf(path+file)
    
    print('Ens %i done'%ens)


# In[ ]:




