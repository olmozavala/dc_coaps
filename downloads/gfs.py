import os
import subprocess
from datetime import datetime
from config.MainConfig import get_config
from config.params import Opts
from os.path import join
from io_utils.io_common import create_folder
import downloads.rdams_client as rc
import os
import xarray as xr
import numpy as np
import pandas as pd

# This file is used to download GFS data from https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl
# Variable information of GFS https://www.nco.ncep.noaa.gov/pmb/products/gfs/ (click on the 'Inventory' links)
# Identifcador https://rda.ucar.edu/datasets/ds084.1/

def download_gfs_archived(cdate, output_folder, forecast_hours=range(24*16), bbox=[0,360, -90, 90]):
    """
    Downloads GFS data for the specified date (always the forecast at 00)
    :param cdate:
    :param forecast_hours
    :param bbox:
    :return:
    """
    # # print(rc.query(['-h']))
    # dsid = 'ds084.1'
    # dsid = 'ds084.3'
    # # dsid = 'ds633.0'
    # param_response = rc.query(['-get_metadata', dsid, '-np']) # All metadata
    # print("Done!")
    # ## Get 3-hour forecast
    # data_3hr_forecast = list(filter(lambda x:x['product'] == '3-hour Forecast',param_response['result']['data']))
    # ## Get Only U and V
    # u_and_V = list(filter(lambda x: x['param'] == 'V GRD' or x['param'] == 'U GRD', data_3hr_forecast))
    # ## Get Only 10 mts abouve sea ground
    # u_and_V_10m = list(filter(lambda x: x['levels']['level'] == 'HTGL' and x['levels']['level_value'] == '10', u_and_V))
    #
    ## Make the request
    dsid = 'ds084.3'
    response = rc.get_control_file_template(dsid)
    template = response['result']['template']
    template_dict = rc.read_control_file(template)
    ##
    template_dict['param'] = 'U GRD/V GRD'
    template_dict['level'] = 'HTGL:10'
    template_dict['date'] = '202105300000/to/202106200000'
    template_dict['product'] = 'Forecast/3-hour'
    template_dict['nlat'] = 70
    template_dict['slat'] = 0
    template_dict['wlon'] = -100
    template_dict['elon'] = 0
    ## Now We can submit a request
    response = rc.submit_json(template_dict)
    assert response['code'] == 200
    print(response)
    print("Success!")

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
        # Only download if we haven't work on those
        if not(os.path.exists(out_file_name)) and not(os.path.exists(out_file_name.replace(".grb","nc"))):
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

    times = pd.date_range(start=c_date, periods=forecast_hours, freq='3H')

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
        ds.close()

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

def gfs_to_cf_netcdf_archived(input_folder, output_folder):
    """
    Filling all the U,V components in a single NetCDF file
    :param input_folder:
    :param c_date:
    :param forecast_hours:
    :return:
    """

    file_names = [x for x in os.listdir(input_folder) if x.find("f000") != -1 and x[-4:] == 'rib2']
    file_names.sort()

    # Iterating over all the files
    for c_file in file_names:
        print(F"Working with {c_file}")
        c_date = datetime.strptime(c_file.split('/')[-1].split('.')[2][0:8], "%Y%m%d")
        times = pd.date_range(start=c_date, periods=1, freq='3H')
        ds = xr.open_dataset(join(input_folder,c_file), engine="cfgrib")
        dims = ds.u.shape
        u = np.zeros((len(times), dims[0], dims[1]))
        v = np.zeros((len(times), dims[0], dims[1]))
        lat = ds.latitude
        lon = ds.longitude
        u[0,:,:] = ds.u
        v[0,:,:] = ds.v
        ds.close()
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

        file_name = join(output_folder, F"{c_date.strftime('%Y-%m-%d')}.nc")
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

##
if __name__ == "__main__":
    # Only for testing
    config = get_config()

    # This is just to merge 'archived' datat into a single netcdf file
    input_folder = "/home/olmozavala/Downloads/test"
    output_folder = join(config[Opts.winds_folder],"Archived")
    gfs_to_cf_netcdf_archived(input_folder, output_folder)
    exit()

    date_range = pd.date_range("2021-10-01", periods=5)
    # This section downloads and merges forecast files into a single netcdf file
    for c_date_pd in date_range:
        c_date = pd.to_datetime(c_date_pd)
        forecast_hours = range(0,24*10+1,3) # Define how many hours we want to download
        bbox=config[Opts.bbox]
        output_folder=join(config[Opts.winds_folder],c_date.strftime("%Y_%m_%d"))
        create_folder(output_folder)
        # Download GFS forecast data
        # file_names = download_gfs(c_date, output_folder, forecast_hours=forecast_hours,bbox=bbox)
        # Merge in a single netcdf function
        gfs_to_cf_netcdf(output_folder, c_date, len(forecast_hours))
        # Remove raw files
        remove_raw_files(output_folder)

