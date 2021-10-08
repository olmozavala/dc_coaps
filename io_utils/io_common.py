import os
from os.path import getmtime
from os import walk, listdir
from os.path import join
import pandas as pd

import numpy as np


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

