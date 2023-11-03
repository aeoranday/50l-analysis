"""
Calculate the running sum for a waveform.
"""
import os
import sys
import argparse
import datetime

import numpy as np
import matplotlib.pyplot as plt

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "./figures"

def plot(run_sum, wf, channel, record_id, run_time, run_id, savetype):
    """
    Plot the running sum.
    Uses all other arguments for titling and save name.
    """
    savename = f"run-{run_id}-sum_wf-{channel}_TID-{record_id}_{run_time.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    fig = plt.figure()
    ax1 = plt.gca()
    ax2 = fig.add_axes([0.45, 0.4, 0.4, 0.4])

    ax1.plot(run_sum, color='k')
    ax1.set_title(f"Run {run_id} Running Sum: Record {record_id} Channel {channel}\n{str(run_time)}")
    ax1.set_xlabel("Time ticks (512 ns / tick)")
    ax1.set_ylabel("ADC Count Sum")

    ax2.plot(wf, color='k')
    ax2.set_title("Waveform")
    plt.savefig(savepath)
    plt.close()

def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def parse():
    parser = argparse.ArgumentParser(description="Sum non-cosmic events, plot the resulting heatmap, and save this array.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument("--savetype", type=str, help="File type to save the figure as. Default : svg.", default="svg")
    parser.add_argument("--channel", type=int, help="Channel to operate the running sum on. Default = 24.", default=24)
    parser.add_argument("--record", type=int, help="Trigger Record ID to operate the running sum on. Default = 0.", default=0)

    args = parser.parse_args()

    assert (args.filename[-4:] == "hdf5"), "File name is not an HDF5 data file."
    return args

def mkdirs():
    """
    Check if the save dirs are made. If not, make them.
    """
    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

def main():
    ### Process Arguments
    args = parse()

    filename = args.filename
    savetype = args.savetype
    channel = args.channel
    record_id = args.record

    mkdirs()

    ### Extract Data
    data = fiftyl_toolkit.Data(filename)
    record = data.get_records()[record_id]
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    ### Processing & Plotting
    wf = data.extract(record, channel)[:800] # Limiting time ticks for clarity.
    wf = median_subtraction(wf)
    original_wf = wf.copy()
    for idx in range(1,len(wf)):
        wf[idx] = wf[idx] + wf[idx-1]

    plot(wf, original_wf, channel, record_id, run_time, run_id, savetype)

if __name__ == "__main__":
    main()
