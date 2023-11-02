"""
Plot a single waveform for some trigger ID on a given channel.
"""
import os
import sys
import argparse
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.
FIGURE_PATH = "./figures"
SAVE_PATH = "./saved_arrays"

def median_subtract(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def wf_plot(wf, dt_title, run_id, trig_id, channel, savetype):
    """
    Plot the waveform plot for the given adc.
    """
    savename = f"wf-{channel}_run-{run_id}_TID-{trig_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure()
    plt.plot(wf, 'k')
    #plt.ylim((0,120))
    plt.xlabel("Frames")
    plt.ylabel("ADC Count (Median Shifted)")
    plt.title(f"Run {run_id} Channel {channel} Waveform: Record ID {trig_id} \n{str(dt_title)}")
    plt.savefig(savepath)
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Plot the channel waveform for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("--record", type=int, help="Trigger Record ID to plot. Default: 0.", default=0)
    parser.add_argument("--channel", type=int, help="Channel number to view. Default: 24.", default=24)
    parser.add_argument("--savetype", type=str, help="Figure save type to use. Default: svg.", default="svg")
    return parser.parse_args()

def mkdirs():
    """
    Check if FIGURE_PATH and SAVE_PATH are made. If not, make them.
    """
    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)
    if not os.path.isdir(SAVE_PATH):
        print(f"Saving saved_arrays to {SAVE_PATH}.")
        os.makedirs(SAVE_PATH)

def main():
    ### Process Arguments
    args = parse()

    h5_file_name = args.filename
    record_id = args.record
    channel = args.channel
    savetype = args.savetype

    ### Extract Data
    data = fiftyl_toolkit.Data(h5_file_name)
    records = data.get_records()[record_id]
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    ### Processing & Plotting
    adcs = data.extract(record, channel)
    wf = median_subtract(wf)
    wf_plot(wf, run_time, run_id, record_id, channel, savetype)

    savename = f"wf-{channel}_run-{run_id}_TID-{record_id}_{run_time.strftime(DT_FORMAT)}.npy"
    savepath = os.path.join(SAVE_PATH, savename)
    with open(savepath, 'wb') as f:
        np.save(f, wf)
    sys.exit(0)

if __name__ == "__main__":
    main()
