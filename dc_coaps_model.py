"""
Usage:
  GlobalModel.py <start_date> <end_date> <name>
  GlobalModel.py (-h | --help)
  GlobalModel.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <winds>       Something [default: 3]
"""
from docopt import docopt
from parcels.scripts import *
from datetime import timedelta, datetime
from os.path import join
from config.params import Opts
from config.MainConfig import get_config
import sys
import os
import gc
import functools
import numpy as np
from parcels import FieldSet, Field, JITParticle, ScipyParticle, ParticleSet, ErrorCode, AdvectionRK4
from downloads.io_hycom import read_files, add_Kh
from mykernels.custom_particles import LitterParticle
from mykernels.wl_kernels import AdvectionRK4COAPS, BrownianMotion2D
import time
from distutils.util import strtobool

time_format = "%Y-%m-%d:%H"
time_format_red = "%Y_%m_%d"

def sequential(start_date, end_date, config, name=''):
    """
    Sequential run of the lagrangian model
    :param start_date:
    :param end_date:
    :param config:
    :param name:
    :return:
    """
    dt = config[Opts.dt]
    kh = 1
    output_file = join(config[Opts.output_folder], name)

    run_time = timedelta(seconds=(end_date - start_date).total_seconds())

    # This one should read all the proper file names for currents, winds, waves
    # file_names = read_files(base_folder, years, wind=winds, start_date=start_date, end_date=end_date)
    wind_files, current_files, wave_files = []

    print("Reading drifter locations.....")
    lat0 = 39 + np.random.random(10)*10
    lon0 = -36 + np.random.random(10)*10
    # Reading currents
    print("Reading currents.....", flush=True)
    variables = {'U': 'surf_u', 'V': 'surf_v'}
    dimensions = {'lat': 'latitude', 'lon': 'longitude', 'time': 'time'}
    currents_fieldset = FieldSet.from_netcdf(current_files, variables, dimensions, allow_time_extrapolation=True)
    # Reading winds
    print("Reading winds .....", flush=True)
    variables = {'U': 'surf_u', 'V': 'surf_v'}
    dimensions = {'lat': 'latitude', 'lon': 'longitude', 'time': 'time'}
    winds_field = Field.from_netcdf(wind_files, variables, dimensions, allow_time_extrapolation=True)
    currents_fieldset.add_field(winds_field, 'winds')
    # Reading waves
    print("Reading waves.....", flush=True)
    variables = {'U': 'surf_u', 'V': 'surf_v'}
    dimensions = {'lat': 'latitude', 'lon': 'longitude', 'time': 'time'}
    waves_field = Field.from_netcdf(wave_files, variables, dimensions, allow_time_extrapolation=True)
    currents_fieldset.add_field(waves_field, 'waves')

    # -------  Making syntetic diffusion coefficient
    U_grid = currents_fieldset.U.grid
    lat = U_grid.lat
    lon = U_grid.lon
    # Getting proporcional size by degree
    print("Adding diffusion .....")
    add_Kh(currents_fieldset, lat, lon, kh)

    print("Setting up everything.....")
    particle_class = JITParticle
    pset = ParticleSet(fieldset=currents_fieldset, pclass=particle_class, lon=lon0, lat=lat0, repeatdt=False)
    out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[Opts.output_freq])
    t = time.time()

    print(F"Adding kernels...")
    kernels = pset.Kernel(AdvectionRK4COAPS)
    kernels += pset.Kernel(BrownianMotion2D)

    print(F"Running with {pset.size} number of particles for {run_time}", flush=True)
    pset.execute(kernels,
                 runtime=run_time,
                 dt=dt,
                 output_file=out_parc_file)

    print(F"Done time={time.time()-t}.....")

    print(F"Saving output to {output_file}!!!!!")
    # domain = {'N': 31, 'S': 16, 'E': -76, 'W': -98}
    # pset.show(field=currents_fieldset.U, domain=domain)  # Draw current particles
    out_parc_file.export() # Save trajectories to file

    # out_parc_file.close()
    # del pset
    # del kernels
    # del currents_fieldset
    # # plotTrajectoriesFile(output_file) # Plotting trajectories
    # print("Forcing gc.collect")
    # gc.collect()
    print("Done!!!!!!!!!!!! YEAH BABE!!!!!!!!", flush=True)

if __name__ == "__main__":
    # Some run examples:
    # GlobalModel.py 2010-01-01:0 2010-03-11:0 True False False TEST 10 //Without restart
    # GlobalModel.py 2010-01-21:0 2010-01-31:0 True False False TEST /home/data/UN_Litter_data/output/TEST_2010-01-21_2010-01-31.nc 10  //With restart
    # Parallel run examples with mpirun:
    # mpirun -np 8 python GlobalModel.py 2010-01-01:0 2010-03-11:0 True False False TEST 10 //Without restart
    args = docopt(__doc__, version='Darpa Challenge by COAPS 0.1')
    # print(args)
    start_date = datetime.strptime(args['<start_date>'], "%Y-%m-%d:%H")
    end_date = datetime.strptime(args['<end_date>'], "%Y-%m-%d:%H")
    name = args['<name>']
    config = get_config()
    run_name = "first test"
    sequential(start_date, end_date, config)