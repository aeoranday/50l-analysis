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


FIGURE_PATH = "./figures"


def avg_rms_plot(adc, timestamp, run_id, file_index, num_events, savetype):
    """
    Plot the average RMS plot.
    """
    savename = f"avg-rms_{run_id:04}.{file_index:04}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure(figsize=(6, 4), dpi=300)

    plt.plot(adc, 'ok', ms=2)
#    plt.ylim((0,120))

    plt.title(f"50L {run_id}.{file_index} Average Channel RMS: {num_events} Events\nTimestamp {timestamp}")
    plt.xlabel("Channel")
    plt.ylabel("RMS")

    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()
    return


def rms_plot(adc, timestamp, run_id, file_index, trig_id, savetype):
    """
    Plot the RMS plot for the given adc.
    """
    savename = f"rms_{run_id:04}.{file_index:04}-{trig_id:04}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure(figsize=(6, 4), dpi=300)

    plt.plot(adc, 'k')
    plt.ylim((0,120))

    plt.title(f"50L {run_id}.{file_index}-{trig_id} Channel RMS:\nTimestamp {timestamp}")
    plt.xlabel("Channel")
    plt.ylabel("RMS")

    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()
    return


def parse():
    parser = argparse.ArgumentParser(description="Plot the channel RMS for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("--tqdm", action="store_true", help="Display average RMS progress with tqdm.")
    parser.add_argument("--savetype",  type=str, help="Choose filetype to save plot as. Default: svg.", default="svg")
    parser.add_argument("--map-name", type=str, help="Channel map name to use.")

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
    map_name = args.map_name

    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

    ### Extract Data
    data = fiftyl_toolkit.WIBEthReader(filename, map_name)
    timestamp = data.creation_timestamp
    run_id = data.run_id
    file_index = data.file_index
    records = data.records

    ### Processing & Plotting
    if do_avg:
        adcs_rms = np.zeros((128,))
        num_records = len(records)
        mismatch = 0
        for record in tqdm(records, total=num_records, desc="Record", disable=not do_tqdm):
            try:
                adcs = data.read_record(record)
                adcs_rms += np.std(adcs, axis=0)
            except ValueError:
                mismatch += 1
        adcs_rms /= (num_records - mismatch)
        avg_rms_plot(adcs_rms, timestamp, run_id, file_index, num_records - mismatch, savetype)
        sys.exit(0)
    else:
        record = records[record_id]
        adcs = data.extract(record)
        adcs_rms = np.std(adcs, axis=0)
        rms_plot(adcs_rms, timestamp, run_id, file_index, record_id, savetype)
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
