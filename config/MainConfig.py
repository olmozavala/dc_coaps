from os.path import join
from config.params import Opts
from datetime import timedelta


# main_folder = " /nexsan/people/ddmitry/DARPA"
main_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/DARPA_Challenge/ExampleData"

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

        # Opts.bbox: [0, 70, -100, 0], # minlat, maxlat, minlon, maxlon
        Opts.bbox: [-90, 90, 0, 360], # minlat, maxlat, minlon, maxlon
    }
    return config