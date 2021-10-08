from enum import Enum

class Opts(Enum):
    # Paths to the data
    winds_folder=1
    currents_folder=2
    waves_folder=3
    drifters_obs_folder=4
    drifters_pred_folder=5
    # Model configuration
    start_date=10  # When to start the forecast
    forecast_days=11  # How many days are we going to forecast
    dt=12  # Delta t of the lagrangian model
    output_freq=13 # How often we want to save the locations

    # Used for the downloading process
    bbox=20

    # Outputs
    output_folder=30