"""
Plot a single waveform for some trigger ID on a given channel.
"""
import os
import argparse

import numpy as np
import matplotlib.pyplot as plt

import fiftyl_toolkit


__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"


FIGURE_PATH = "./figures"
SAVE_PATH = "./saved_arrays"


def median_subtract(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')


def wf_plot(wf, timestamp, run_id, file_index, trig_id, channel, savetype):
    """
    Plot the waveform plot for the given adc.
    """
    savename = f"wf-{channel}_{run_id:04}.{file_index:04}-{trig_id:04}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure(figsize=(6, 4), dpi=300)

    plt.plot(wf, 'k')

    plt.title(f"50L {run_id}.{file_index}-{trig_id} Channel {channel} Waveform:\nTimestamp {timestamp}")
    plt.xlabel("Time (512 ns / tick)")
    plt.ylabel("ADC Count (Median Subtracted)")

    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()
    return

def parse():
    parser = argparse.ArgumentParser(description="Plot the channel waveform for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("--record", type=int, help="Trigger Record ID to plot. Default: 0.", default=0)
    parser.add_argument("--channel", type=int, help="Channel number to view. Default: 24.", default=24)
    parser.add_argument("--savetype", type=str, help="Figure save type to use. Default: svg.", default="svg")
    parser.add_argument("--map-name", type=str, help="Channel map name to use.")
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
    return

def main():
    ### Process Arguments
    args = parse()

    h5_file_name = args.filename
    record_id = args.record
    channel = args.channel
    savetype = args.savetype
    map_name = args.map_name

    ### Extract Data
    data = fiftyl_toolkit.Data(h5_file_name, map_name)
    record = data.records[record_id]
    timestamp = data.creation_timestamp
    run_id = data.run_id
    file_index = data.file_index

    ### Processing & Plotting
    wf = data.extract(record, channel)
    wf = median_subtract(wf)
    wf_plot(wf, timestamp, run_id, file_index, record_id, channel, savetype)

    savename = f"wf-{channel}_{run_id:04}.{file_index:04}-{record_id:04}.npy"
    savepath = os.path.join(SAVE_PATH, savename)
    with open(savepath, 'wb') as f:
        np.save(f, wf)
    return


if __name__ == "__main__":
    main()
