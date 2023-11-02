"""
Create a histogram of max ADC counts for waveforms.
"""
import os
import sys
import argparse
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "./figures"
SAVE_PATH = "./saved_arrays"

def median_subtraction(adcs):
    """
    Median subtract an ADCs matrix.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def get_extrema(adcs, ext_operator):
    """
    Get the extrema for each waveform in adcs.
        adcs
            2D array of (channels, time)
        ext_operator
            Extrema operator to use: can be np.max or np.min
    Returns
        1D array of (channels,) with extrema values.
    """
    return ext_operator(adcs, axis=1)


def plot_hist(extrema, dt_title, run_id, ext_str, channel, savetype="svg"):
    """
    Plot a histogram of extrema values.
        extrema
            1D array of (channels,) to plot
        dt_title
            datetime object to use for save name and titling.
        run_id
            Run ID of the data.
        ext_str
            String of either 'Maximum' or 'Minimum' for the operator that was used.
        channel
            Integer of which channel this focuses on.
        savetype
            String of the format to save the plot as
    """
    save_name = f"selective_extrema-{ext_str[:3].lower()}_ch{channel}_hist_{dt_title.strftime(DT_FORMAT)}.{savetype}"

    if ext_str.lower()[:3] == "max":
        bins = range(0,150,5)
    elif ext_str.lower()[:3] == "min":
        bins = range(-150,0,5)
    else:
        bins = None

    plt.figure()
    plt.hist(extrema, bins=bins, color='k')
    plt.title(f"Channel {channel} {ext_str} ADC Histogram:\n Run {run_id} {dt_title}")
    plt.xlabel("ADC Count")
    plt.ylabel("Count")
    plt.savefig(os.path.join(FIGURE_PATH, save_name))

def parse():
    parser = argparse.ArgumentParser(description="Plot a histogram of ADC count extrema.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument("--savetype", type=str, help="Specify the format to save the figure as. Default: svg.", default="svg")
    parser.add_argument("--channel", type=int, help="Specify which channel to generate the histogram from.", default=24)

    return parser.parse_args()

def mkdirs():
    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)
    if not os.path.isdir(SAVE_PATH):
        print(f"Saving arrays to {SAVE_PATH}.")
        os.makedirs(SAVE_PATH)

def save_hist(extrema, dt_title, ext_str, channel):
    """
    Save np.array of extrema to SAVE_PATH.
        extrema
            np.array to save.
        dt_title
            datetime format to use in file naming.
        ext_str
            String of either "Minimum" or "Maximum"
        channel
            The channel that was singled out
    """
    save_name = f"selective_extrema-{ext_str[:3].lower()}_ch{channel}_hist_{dt_title.strftime(DT_FORMAT)}.npy"
    with open( os.path.join(SAVE_PATH, save_name), 'wb' ) as f:
        np.save(f, extrema)

def main():
    args = parse()

    ### Staging
    h5_filename = args.filename
    savetype = args.savetype
    channel = args.channel

    mkdirs()

    ### Getting data
    data = fiftyl_toolkit.Data(h5_filename)
    records = data.get_records()
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    max_array = np.zeros(len(records))
    min_array = np.zeros(len(records))
    mismatch_cnt = 0
    for idx, record in enumerate(records):
        try:
            adcs = data.extract(record)
            wf = median_subtraction(adcs)[:800, channel] # Limiting total window size for now.
            max_val = np.max(wf)
            max_idx = np.where(wf == max_val)[0][0]
            min_val = np.min( wf[max_idx:(max_idx+50)] )
            max_array[idx] = max_val
            min_array[idx] = min_val
        except ValueError:
            mismatch_cnt += 1

    ### Analysis/Processing & Plotting
    # Waveforms that have a shape mismatch did not get updated, so remove those entries.
    max_array = max_array[max_array != 0]
    min_array = min_array[min_array != 0]

    plot_hist(max_array, run_time, run_id, "Maximum", channel, savetype)
    save_hist(max_array, run_time, "Maximum", channel)
    plot_hist(min_array, run_time, run_id, "Minimum", channel, savetype)
    save_hist(min_array, run_time, "Minimum", channel)

    sys.exit(0)

if __name__ == "__main__":
    main()
