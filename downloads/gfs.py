import os
import subprocess
from datetime import datetime
from config.MainConfig import get_config
from config.params import Opts
from os.path import join
from io_utils.io_common import create_folder
import os
import xarray as xr
import numpy as np
import pandas as pd

# This file is used to download GFS data from https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl
# Variable information of GFS https://www.nco.ncep.noaa.gov/pmb/products/gfs/ (click on the 'Inventory' links)
# It does it with wget of multiple files

def download_gfs(cdate, output_folder, forecast_hours=range(24*16), bbox=[0,360, -90, 90]):
    """
    Downloads GFS data for the specified date (always the forecast at 00)
    :param cdate:
    :param forecast_hours
    :param bbox:
    :return:
    """
    urls = []
    date_str = cdate.strftime("%Y%m%d")
    out_file_names = []
    # Generating the proper urls
    for c_hour in forecast_hours:
        out_file_name = join(output_folder,F"{date_str}_{c_hour:03d}.grb")
        out_file_names.append(out_file_name)
        if not(os.path.exists(out_file_name)):
            c_url = F"\"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f{c_hour:03d}&lev_10_m_above_ground=on&all_var=on&subregion=&leftlon={bbox[2]}&rightlon={bbox[3]}&toplat={bbox[1]}&bottomlat={bbox[0]}&dir=%2Fgfs.{date_str}%2F00%2Fatmos\" -O {out_file_name}"
            urls.append(c_url)

    # Downloading with WGET
    for c_url in urls:
        tocall = F"wget {c_url}"
        print(F"Running {tocall}")
        subprocess.call([tocall],shell=True)

    return out_file_names

def gfs_to_cf_netcdf(input_folder, c_date, forecast_hours):
    """
    Filling all the U,V components in a single NetCDF file
    :param input_folder:
    :param c_date:
    :param forecast_hours:
    :return:
    """

    times = pd.date_range(start=c_date, periods=forecast_hours, freq='H')

    file_names = [join(input_folder,x) for x in os.listdir(input_folder) if x[-3:] == 'grb']
    file_names.sort()

    # Iterating over all the files
    for i, c_file in enumerate(file_names):
        ds = xr.open_dataset(join(input_folder,c_file), engine="cfgrib")
        if i == 0:
            dims = ds.u10.shape
            u = np.zeros((len(times), dims[0], dims[1]))
            v = np.zeros((len(times), dims[0], dims[1]))
            lat = ds.latitude
            lon = ds.longitude
        u[i,:,:] = ds.u10
        v[i,:,:] = ds.v10

    # Create a CF-Compliante NetCDF from grb
    u_da = xr.DataArray(u, dims=['time','lat', 'lon'])
    v_da = xr.DataArray(v, dims=['time','lat', 'lon'])

    ds_nc = xr.Dataset(
        {
             "U": (("time", "lat", "lon"), u_da.data),
             "V": (("time", "lat", "lon"), v_da.data),
                },
        {"time": times, "lat": lat.data, "lon": lon.data},
    )

    file_name = join(input_folder, F"{c_date.strftime('%Y-%m-%d')}.nc")
    ds_nc.to_netcdf(file_name)
    print("Done!")

def remove_raw_files(input_folder):
    """
    Removes raw files downloaded from GFS
    :param input_folder:
    :return:
    """
    file_names = [join(input_folder,x) for x in os.listdir(input_folder) if  x[-3:] == 'grb' or x[-3:] == 'idx']
    for c_file in file_names:
        print(F"Removing file {c_file}")
        os.remove(c_file)

if __name__ == "__main__":
    # Only for testing
    config = get_config()

    # date_range = pd.date_range("2021-05-30", periods=30)
    date_range = pd.date_range("2021-10-01", periods=1)
    for c_date_pd in date_range:
        c_date = pd.to_datetime(c_date_pd)
        forecast_hours = range(24*10) # Define how many hours we want to download
        bbox=config[Opts.bbox]
        output_folder=join(config[Opts.winds_folder],c_date.strftime("%Y_%m_%d"))
        create_folder(output_folder)
        # Download GFS forecast data
        file_names = download_gfs(c_date, output_folder, forecast_hours=forecast_hours,bbox=bbox)
        # Merge in a single netcdf function
        gfs_to_cf_netcdf(output_folder, c_date, len(forecast_hours))
        # Remove raw files
        remove_raw_files(output_folder)
