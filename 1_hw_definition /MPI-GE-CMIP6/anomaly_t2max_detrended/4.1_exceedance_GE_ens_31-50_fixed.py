#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
percentile = 90

#Definition type: daily moving threshold (mov_day) or JA moving threshold (mov_JA)
def_type = 'fix_day' #'mov_JA'


# In[3]:


#Define run
run_type = ['HIST','ssp119','ssp126','ssp245','ssp370','ssp585']
#run_type = ['HIST','ssp126','ssp245','ssp585']
#run_type = ['ssp119','ssp370']


# In[4]:


def run_hw_exceed(ens,run_type):  
    ens_total = 30 + ens
    
    #import data
    path = '/work/uo1075/u241308/data_python_PostDoc/MPI_GE_cmip6/t2max/'
    file = 'nGE_Tmax_'+ run_type +'_dm_ens_31-50_land_europe_ens_mean_anomaly_detrend.nc'
    
    #load t2max
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
        threshold_complete = copy.deepcopy(data1)
        threshold_complete[:,:,:] = np.tile(threshold,(year_number,1,1))
        
    #load hw_detect
    path = '/work/uo1075/u241308/data_python/HW_extension/GE_cmip6/anomaly/hw_detect/'+run_type+'/'
    file = 'hw_detect_%id'%c_days +'_%s'%percentile+ '_' + def_type + '_GE_'+ run_type +'_ref_%i'%ref_min + '-%i'%ref_max + '_ensemble_%i_anomaly_detrend.nc'%ens_total    
    
    with xr.open_dataset(path+file) as hw_detect:
        hw_detect = hw_detect.tasmax
        
    #Compute exceedance
    data_exceed = data1 - threshold_complete
    data_exceed = xr.where(hw_detect==1,data_exceed,0)
    
    #longitude weight: cosine of the latitude
    grid_weight2 = np.zeros((len(data1.lat),len(data1.lon)))
    for y in range(0,len(data1.lat)):
        grid_weight2[y,:] = cos(radians(data1.lat[y]))
    grid_weight2 = np.repeat(grid_weight2[np.newaxis,:,:],data_exceed.shape[0],axis=0)
    
    #weight the grid exceedance
    data_exceed_weighted = copy.deepcopy(data_exceed)
    data_exceed_weighted[:,:,:] = np.multiply(data_exceed,grid_weight2)
    
    #Define new longitudes: from 0,360 to -180,180
    data_exceed_weighted['lon'] = np.where(data_exceed_weighted.lon >180, data_exceed_weighted.lon-360,data_exceed_weighted.lon)
    ind = np.argsort(data_exceed_weighted.lon)
    ind.values
    data_exceed_weighted = data_exceed_weighted[:,:,ind.values]
                
    return data_exceed_weighted


# In[ ]:


run = 5 #select run type: HIST,ssp126...
#ens_number = 20 #total number of ensembles
ens_start = 0
ens_end = 20

#for ens in range(ens_number):
for ens in range(ens_start,ens_end):
    ens_total = ens + 30
    hw_exceed = run_hw_exceed(ens,run_type[run])
    
    #save data
    path = '/work/uo1075/u241308/data_python/HW_extension/GE_cmip6/anomaly/hw_exceed/'+run_type[run]+'/'
    file = 'data_exceed_lonlat_weighted_%s' %percentile + 'pct_%s' %c_days + 'd_' + def_type + '_GE_'+run_type[run]+'_ref_%i'%ref_min + '-%i'%ref_max + '_ensemble_%i_anomaly_detrend.nc'%ens_total  
    hw_exceed.to_netcdf(path+file)
    
    print('Ens %i done'%ens)


# In[ ]:




