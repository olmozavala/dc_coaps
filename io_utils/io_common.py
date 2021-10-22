import os
from datetime import timedelta, datetime
from os.path import getmtime
from os import walk, listdir
from os.path import join
import pandas as pd
from config.params import Opts
import matplotlib.pyplot as plt

import numpy as np
import scipy.interpolate as interpolate


def create_folder(output_folder):
    """ It simply verifies if a folder already exists, if not it creates it"""
    if not(os.path.exists(output_folder)):
        os.makedirs(output_folder)

def get_latest_file(file_paths):
    """
    From a list of files it chooses the latest one (the closest to current date)
    :param file_paths:
    :return:
    """
    latest_file = ''
    largest_date = -1
    for cur_file in file_paths:
        cur_time = getmtime(cur_file)
        if cur_time > largest_date:
            largest_date = cur_time
            latest_file = cur_file

    return latest_file

def read_splits_file(file_name):
    """Reads a splits file and returns the ids for training, validation and test"""
    splits_df = pd.read_csv(file_name)
    train_ids = splits_df.iloc[:,0]
    val_ids = splits_df.iloc[:,1][splits_df.iloc[:,1] != -1]
    test_ids = splits_df.iloc[:,2][splits_df.iloc[:,2] != -1]

    return train_ids.values, val_ids.values, test_ids.values

def read_test_data_files(config):
    currents_folder = join(config[Opts.currents_folder], "202105")
    winds_folder = join(config[Opts.winds_folder], "TestPeriod")
    waves_folder = config[Opts.waves_folder]

    current_files = [join(currents_folder,x) for x in os.listdir(currents_folder)]
    winds_files = [join(winds_folder,x) for x in os.listdir(winds_folder)]
    waves_files = [join(waves_folder,x) for x in os.listdir(waves_folder) if x.find("test_period") != -1]

    current_files.sort()
    winds_files.sort()

    return current_files, winds_files, waves_files

def parse_drifters_dates(dates):
    """
    This function is in charge of reading the data from the drifters csv file
    :param dates:
    :return:
    """
    ret_dates = [datetime.strptime(F"{x[0:19]}", "%Y-%m-%d %H:%M:%S") for x in dates]
    return ret_dates

def parse_drifters_dates_by_hour(dates):
    """
    This function is in charge of reading the data from the drifters csv file
    :param dates:
    :return:
    """
    # print([x[0:13] for x in dates])
    ret_dates = [datetime.strptime(F"{x[0:13]}", "%Y-%m-%d %H") for x in dates]
    return ret_dates

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    return list(map(lambda dt: int((dt - epoch).total_seconds()), dt))

# interpolate the position at a specific time
def interpolate_drifters_time(t):
    # read data
    file_name = '/nexsan/people/ddmitry/DARPA/drifters_obs/challenge_30-days_sofar_20210530_atlantic_sample.csv'
    df = pd.read_csv(file_name, names=['sig', 'peakper', 'meanper', 'peakdir', 'peakdirspre', 'meandir',
                                           'meandirspread', 'time', 'lat', 'lon', 'epoch', 'id'], header=0,
                                         usecols=[7,8,9,10,11], parse_dates=['time'])

    # indices of trajectory
    nb_drifters = df['id'].unique()

    if len(t) > 1:
        x_t = np.zeros((len(nb_drifters),len(t)))
        y_t = np.zeros((len(nb_drifters),len(t)))
    else:
        x_t = np.zeros(len(nb_drifters))
        y_t = np.zeros(len(nb_drifters))

    for key, drifter in df.groupby('id'):
        # retrieve trajectory
        t_i = drifter['epoch']
        x_i = drifter['lon']
        y_i = drifter['lat']

        # interpolate
        flon = interpolate.interp1d(t_i, x_i)
        flat = interpolate.interp1d(t_i, y_i)
        x_t[key] = flon(t)
        y_t[key] = flat(t)
    return x_t, y_t

if __name__ == "__main__":
    # Testing the interpolatin
    dates = np.array([datetime(2021, 5, 30, 1, 0, 0)])
    times = unix_time(dates)
    x0, y0 = interpolate_drifters_time(times)
    x = 1