from os.path import join
from config.params import Opts
from datetime import timedelta


main_folder = " /nexsan/people/ddmitry/DARPA"

def get_config():
    config= {
        # Paths
        Opts.currents_folder: join(main_folder,"currents"),
        Opts.winds_folder: join(main_folder,"winds"),
        Opts.waves_folder: join(main_folder,"waves"),
        Opts.drifters_obs_folder: join(main_folder,"drifters_obs"),
        Opts.drifters_pred_folder: join(main_folder,"drifters_predict"),
        # Opts.output_folder: join(main_folder,"drifters_pred"),
        # Model
        Opts.dt: timedelta(hours=1), # 1 hour
        Opts.output_freq: timedelta(hours=24),  # 24
        # GlobalModel.repeat_release: timedelta(hours=0),  # 61

        Opts.bbox: [0, 30, -99, -49], # minlat, maxlat, minlon, maxlon
    }
    return config