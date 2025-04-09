#!/usr/bin/env python
# coding: utf-8

# In[7]:


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


# In[8]:

model = 'CanESM5'
ens_number2 = '50'
ens_number = 50

#reference time
ref_min = 1985
ref_max = 2014

# Consecutive days for heatwave detection
c_days = 6

# Threshold percentile
percentile = 90#95 #90

#Definition type: daily moving threshold (mov_day) or JA moving threshold (mov_JA)
def_type = 'fix_day' #'mov_JA'

#Define run
run_type = ['historical','ssp245','ssp585']

# In[10]:


def run_hw_detect(ens,run_type):    
    #import data
    path = '/work/uo1075/u241308/SMILE/'+model+'/tasmax/'
    file = model+'_Tmax_'+run_type+'_dm_ens_1-'+ens_number2+'_GEgrid_land_europe_anomaly_detrend.nc'
    
    with xr.open_dataset(path+file) as data1:
        data1 = data1.tasmax
    
        #Select ensemble members
        data1 = data1[:,ens,:,:]
        
        #Get rid off 29th of februarys
        data1 = data1.sel(time=~((data1.time.dt.month == 2) & (data1.time.dt.day == 29)))
        
    #load threshold
    path = '/work/uo1075/u241308/data_python/HW_extension/'+model+'/anomaly_detrended/threshold/'
    file = 'threshold_%s'%percentile+ '_' + def_type +'_'+model+'_ref_%i'%ref_min + '-%i'%ref_max + '_ensemble_%i_anomaly_detrend.nc'%ens     
    
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


# In[ ]:

for run in np.arange(len(run_type)):
    for ens in np.arange(ens_number):
        hw_detect = run_hw_detect(ens,run_type[run])
        
        #save data
        path = '/work/uo1075/u241308/data_python/HW_extension/'+model+'/anomaly_detrended/hw_detect/'
        file = 'hw_detect_%id'%c_days +'_%s'%percentile+ '_' + def_type + '_'+model+'_'+ run_type[run] +'_ref_%i'%ref_min + '-%i'%ref_max + '_ensemble_%i_anomaly_detrend.nc'%ens     
        hw_detect.to_netcdf(path+file)
        
        print('Ens %i done'%ens)
    

# In[ ]:




