# External
import numpy as np
import pandas as pd
import xarray as xr
import  pyproj
import holoviews as hv
from holoviews import opts
from pyproj import CRS, Geod
from datetime import timedelta, datetime
# Common
# This project
from config.params import Opts
from config.MainConfig import get_config
from io_utils.io_common import read_test_data_files, parse_drifters_dates_by_hour, interpolate_drifters_time, unix_time

hv.extension('matplotlib')
##
print("Reading predicted data...", flush=True)
file_name = "/nexsan/people/ddmitry/DARPA/drifters_predict/hycom/current/forecast_t0_202105301200.nc"
ds_pred_xr = xr.open_dataset(file_name)
ds_pred = pd.DataFrame(data={'time': ds_pred_xr.time.values.flatten(),
                             'lat':ds_pred_xr.lat.values.flatten(),
                             'lon':ds_pred_xr.lon.values.flatten(),
                             'id':ds_pred_xr.trajectory.values.flatten()})
ds_pred
by_time_pred = ds_pred.groupby('time')

by_time_pred.groups
hm_data = {}
hm_distances = {}
count = 0
tot_ids = len(by_time_pred)
geod = CRS("epsg:4326").get_geod()
for id, c_time_pred in by_time_pred:
    c_time_pred = by_time_pred.get_group(id)
    lat_lon_pred = (c_time_pred['lon'], c_time_pred['lat'])
    lat_lon_obs = interpolate_drifters_time(unix_time([id]))
    distances = [geod.line_length([lat_lon_obs[1][i], lat_lon_pred[1].iloc[i]],
                                  [lat_lon_obs[0][i], lat_lon_pred[0].iloc[i]])/1000 for i in range(len(lat_lon_obs[0]))]

    hpoints_obs = hv.Points(lat_lon_obs, label='Obs').opts(s=80)
    hpoints_pred = hv.Points(lat_lon_pred, label='Pred').opts(c='red', marker='+')
    # hm_data[id] = hpoints_obs * hpoints_pred
    # y_dim = hv.Dimension('km', range=(0,100))
    # hm_distances[id] = hv.Scatter(distances, 'id', vdims=y_dim, label="Distances")
    fig = hv.render(hpoints_obs * hpoints_pred)
    fig.show()

print("Done!")
#%%
# lat_lon_obs.shape
# hv.HoloMap(hm_data, kdims='Time').opts(title='Locations')  + hv.HoloMap(hm_distances, kdims='Time')

#%%
