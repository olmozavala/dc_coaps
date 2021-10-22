# External
import pandas as pd
from cartopy import crs
import numpy as np
from os.path import join
import os
import xarray as xr
import datetime
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
# import holoviews as hv
# import geoviews.feature
# import geoviews as gv
# from geoviews import opts
# import geoviews.feature as gf
# from holoviews.operation.datashader
# import datashader, shade, dynspread, spread, rasterize
# from holoviews.operation import decimate
# Common
from io_utils.io_common import parse_drifters_dates
# This project
from config.MainConfig import get_config
from config.params import Opts

# gv.extension('matplotlib')

config = get_config()

def get_currents(c_time, des_lats, des_lons):
    folder = join(config[Opts.currents_folder], '202105')
    all_files = os.listdir(folder)
    all_dates = np.array([datetime.strptime(x[15:30],"%Y%m%d12_t0%H") for x in all_files])
    closest_time_idx = np.argmin([np.abs(x-c_time) for x in all_dates])
    closest_file = all_files[closest_time_idx]
    print(F"{c_time} vs {closest_file}")
    # TODO INTERPOLATE CURRENTS
    currents = xr.open_dataset(join(folder, closest_file))
    currents['lat'] = currents.latitude.data
    currents['lon'] = currents.longitude.data
    interp_currents = currents.interp(lat=des_lats, lon=des_lons)
    u = interp_currents.surf_u[0,:,:].data
    v = interp_currents.surf_v[0,:,:].data
    return u, v, datetime.strptime(closest_file[15:30],"%Y%m%d12_t0%H")

def get_winds(des_time, des_lats, des_lons):
    file_name = "/nexsan/people/ddmitry/DARPA/winds/navgem_0.5_test_period.nc"
    winds = xr.open_dataset(file_name)
    interp_winds = winds.interp(time=des_time, latitude=des_lats, longitude=des_lons)
    u = interp_winds.wnd_ucmp_height_above_ground.data[0,:,:]
    v = interp_winds.wnd_vcmp_height_above_ground.data[0,:,:]
    return u, v

def evaluate_currents(ds):
    grp_by_drifter = ds.groupby('id')
    # Iterates all the drifters by id
    num_next_pos = 6
    rand_ids = np.arange(0,len(ds))
    np.random.shuffle(rand_ids)
    for i in rand_ids:
        id_drifter = ds.iloc[i]['id']
        c_drifter = grp_by_drifter.get_group(id_drifter)
        id_time = np.random.randint(0,len(c_drifter)-num_next_pos, 1)[0]
        row = c_drifter.iloc[id_time]
        c_time = row['time']
        drifter_lat = row.lat
        drifter_lon = row.lon
        domain_size = .2  # in degrees
        grid_pts = 10
        y = np.linspace(drifter_lat-domain_size/2, drifter_lat+domain_size/2, grid_pts)  # lons
        x = np.linspace(drifter_lon-domain_size/2, drifter_lon+domain_size/2, grid_pts)  # lons
        u, v, currents_time = get_currents(c_time, y, x)
        uw, vw = get_winds(c_time, y, x)
        # Select the next x positions
        lats = c_drifter.lat.values[id_time:id_time+num_next_pos]
        lons = c_drifter.lon.values[id_time:id_time+num_next_pos]
        plt.streamplot(x, y, u, v, color='#2A9D8F',linewidth=2)
        plt.streamplot(x, y, uw, vw, color='#E9C46A', linewidth=1, arrowsize=1)
        plt.scatter(lons, lats, c='r', s=15)
        plt.scatter(lons[0], lats[0], c='k', s=15, label=F"Start: {c_time}")
        plt.scatter(lons[-1], lats[-1], c='g', s=15, label=F"End: {c_drifter.time.values[id_time+num_next_pos]}")
        plt.title(F"id {id_drifter} \n drifter_time {c_time} \n currents_time {currents_time}")
        plt.legend(loc='upper center')
        file_name = join("/data/DARPA/SuperResolution/Imgs/analyze_currents_wind_stokesdrift",F"id_{id_drifter}_time_{c_time}")
        plt.savefig(file_name)
        plt.close()
        # plt.show()

print("Reading data...")
file_drifters = join(config[Opts.drifters_obs_folder],os.listdir(config[Opts.drifters_obs_folder])[0])
ds = pd.read_csv(file_drifters, header=0, names=['sigwaveheight','peakperiod', 'meanperiod','peakdirection','dirspread', 'meandirection',
                                                 'meandirectionspread','time','lat','lon','epoch','id'],
                                         parse_dates=['time'], date_parser=parse_drifters_dates)

evaluate_currents(ds)

# bydrifter = ds.groupby('id')
# print("Plotting drifter data...")
# # Obtains the positions that are closest to the desired start time
#
# for id, c_drifter in bydrifter:
#     print(F"Reading id:{id}")
#     lats = c_drifter['lat'].values
#     lons = c_drifter['lon'].values
#     if id == 0:
#         loc = gv.Points((lons, lats))
#     else:
#         loc *= gv.Points((lons, lats))
#         break
#
# print("plotting....")
# # full_world = (gf.ocean * gf.land * gf.coastline * gf.borders)
# # p1 = (loc * gf.land).opts('feature', projection=crs.PlateCarree())
# p1 = decimate(loc)
# fig = gv.render(p1)
# fig.show()
# print("Done!")