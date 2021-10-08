import numpy as np
import subprocess
from datetime import datetime, timedelta
import xarray as xr
import matplotlib.pyplot as plt

def download_gfs(cdate, forecast_hours=range(24*16), bbox=[0,360, -90, 90]):
    urls = []
    date_str = cdate.strftime("%Y%M%d")
    # Generating the proper urls
    for c_hour in forecast_hours:
        c_url = F"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f{c_hour:03d}&lev_10_m_above_mean_sea_level=on&lev_surface=on&var_VGRD=on&leftlon={bbox[0]}&rightlon={bbox[1]}&toplat={bbox[3]}&bottomlat={bbox[2]}&dir=%2Fgfs.{date_str}%2F00%2Fatmos"
        urls.append(c_url)

    # Downloading with WGET
    for c_url in urls:
        tocall = F"wget {c_url}"
        print(F"Running {tocall}")
        subprocess.call([tocall],shell=True)

if __name__ == "__main__":
    # Only for testing
    c_date = datetime.strptime("2021-10-07","%Y-%M-%d")
    forecast_hours = range(24*2) # Define how many hours we want to download
    bbox=[0,360, -90, 90]
    print(download_gfs(c_date, forecast_hours=forecast_hours))
