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

def plot(run_sum, wf, channel, record_id, run_time, run_id, savetype='svg', mini_wf=False):
    """
    Plot the running sum. Optionally, plot the original waveform if mini_wf is true.
        run_sum
            Running sum array to be plotted.
        wf
            Original waveform to be optionally plotted.
        channel
            Channel number that this running sum is from.
        record_id
            Trigger Record ID of the original waveform.
        run_time
            datetime object of when the run happened.
        run_id
            Run ID.
        savetype
            Figure image type to save as.
        mini_wf
            Option to include a mini-figure of the original waveform.
    Uses all other arguments for titling and save name.
    """
    savename = f"run-{run_id}-sum_wf-{channel}_TID-{record_id}_{run_time.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    fig = plt.figure()
    ax1 = plt.gca()

    ax1.plot(run_sum, color='k')
    ax1.set_title(f"Run {run_id} Running Sum: Record {record_id} Channel {channel}\n{str(run_time)}")
    ax1.set_xlabel("Time ticks (512 ns / tick)")
    ax1.set_ylabel("ADC Count Sum")

    if mini_wf:
        ax2 = fig.add_axes([0.45, 0.4, 0.4, 0.4])
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
    parser.add_argument("--mini", action="store_true", help="Include a mini-figure of the original waveform. Default = False.")

    args = parser.parse_args()

    assert (args.filename[-4:] == "hdf5"), "File name is not an HDF5 data file."
    return args

def mkdirs(path):
    """
    Check if the save dirs are made. If not, make them.
    """
    if not os.path.isdir(path):
        print(f"Saving figures to {path}.")
        os.makedirs(path)

def main():
    ### Process Arguments
    args = parse()

    filename = args.filename
    savetype = args.savetype
    channel = args.channel
    record_id = args.record
    mini_wf = args.mini

    if mini_wf:
        global FIGURE_PATH
        FIGURE_PATH += '/mini-wf'

    mkdirs(FIGURE_PATH)

    ### Extract Data
    data = fiftyl_toolkit.Data(filename)
    record = data.get_records()[record_id]
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    ### Processing & Plotting
    wf = data.extract(record, channel)
    wf = median_subtraction(wf)
    original_wf = wf.copy()
    for idx in range(1,len(wf)):
        wf[idx] = wf[idx] + wf[idx-1]

    plot(wf, original_wf, channel, record_id, run_time, run_id, savetype, mini_wf)

if __name__ == "__main__":
    main()
