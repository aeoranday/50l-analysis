"""
Plot a single RMS plot for some trigger ID.
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

def avg_rms_plot(adc, dt_title, run_id, num_events, savetype):
    """
    Plot the average RMS plot.
    """
    savename = f"avg-rms_run-{run_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure()
    plt.plot(adc, 'k')
    plt.ylim((0,120))
    plt.xlabel("Channels")
    plt.ylabel("RMS")
    plt.title(f"Run {run_id} Channel Average RMS: {num_events} Events\n{str(dt_title)}")
    plt.savefig(savepath)
    plt.close()

def rms_plot(adc, dt_title, run_id, trig_id, savetype):
    """
    Plot the RMS plot for the given adc.
    """
    savename = f"rms_run-{run_id}_TID{trig_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure()
    plt.plot(adc, 'k')
    plt.ylim((0,120))
    plt.xlabel("Channels")
    plt.ylabel("RMS")
    plt.title(f"Run {run_id} Channel RMS: Trigger ID {trig_id} \n{str(dt_title)}")
    plt.savefig(savepath)
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Plot the channel RMS for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("--tqdm", action="store_true", help="Display average RMS progress with tqdm.")
    parser.add_argument("--savetype",  type=str, help="Choose filetype to save plot as. Default: svg.", default="svg")

    record_or_avg = parser.add_mutually_exclusive_group()
    record_or_avg.add_argument("--record", type=int, help="Trigger Record ID to plot.", default=-1)
    record_or_avg.add_argument("--avg", action="store_true", help="Plot the average RMS for all records.")
    args = parser.parse_args()
    if (args.record == -1 and not args.avg): # If neither are specified, default to using the average.
        args.avg = True
    return args

def main():
    ### Process Arguments
    args = parse()

    filename = args.filename
    record_id = args.record
    do_avg = args.avg
    do_tqdm = args.tqdm
    savetype = args.savetype

    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

    ### Extract Data
    data = fiftyl_toolkit.Data(filename)
    run_time = data.get_datetime()
    run_id = data.get_run_id()
    records = data.get_records()

    ### Processing & Plotting
    if do_avg:
        adcs_rms = np.zeros((128,))
        num_records = len(records)
        mismatch = 0
        for record in tqdm(records, total=num_records, desc="Record", disable=not do_tqdm):
            try:
                adcs = data.extract(record)
                adcs_rms += np.std(adcs, axis=0)
            except ValueError:
                mismatch += 1
        adcs_rms /= (num_records - mismatch)
        avg_rms_plot(adcs_rms, run_time, run_id, num_records - mismatch, savetype)
        sys.exit(0)
    else:
        record = records[record_id]
        adcs = data.extract(record)
        adcs_rms = np.std(adcs, axis=0)
        rms_plot(adcs_rms, run_time, run_id, record_id, savetype)
        sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    main()
