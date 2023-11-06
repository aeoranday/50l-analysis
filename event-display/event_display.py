"""
Plot a single snapshot (may contain nothing of note).
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

DT_FORMAT = "%Y%m%dT%H%M%S"

def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def subplot(adcs, dt_title, run_id, trig_id, savetype):
    """
    Plot 3-pane ADCs for each of the 3 planes.
        adcs
            2D array of ADCs to be plotted.
        dt_title
            datetime format of when the snapshot took place; used in the plot title.
        run_id
            Run ID of the data file.
        trig_id
            Trigger ID; used in the plot title.
        savetype
            Image format to save as.
    """
    savename = f"50l-subplots-snapshot_TID{trig_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    save_path = os.path.join(FIGURE_PATH, savename)

    plane_channels = (("Collection", np.arange(0, 48)),
                    ("Induction 1", np.arange(48, 88)),
                    ("Induction 2", np.arange(88, 128)))

    f, ax = plt.subplots(1,3, sharey=True)
    plt.suptitle(f"50L Run {run_id} Snapshot: {dt_title} -- Trigger ID {trig_id}")
    for idx, (plane, channels) in enumerate(plane_channels):
        z_plot = ax[idx].imshow(adcs[:, channels], origin='lower')
        ax[idx].set_title(plane)
        plt.colorbar(z_plot, ax=ax[idx])
        ax[idx].set_aspect(len(channels) / FRAMES_PER_RECORD)
    f.supxlabel("Channels")
    f.supylabel("Time tick (512 ns / tick)")
    f.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot(adcs, dt_title, run_id, trig_id, savetype):
    """
    Plot ADCs in the traditional 50L heatmap plot format.
        adcs
            2D array of ADCs to be plotted.
        dt_title
            datetime format of when the snapshot took place; used in the plot title.
        run_id
            Run ID of the data file.
        trig_id
            Trigger ID; used in the plot title.
        savetype
            Image format to save as.
    """
    savename = f"50l-snapshot_TID{trig_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    save_path = os.path.join(FIGURE_PATH, savename)

    plt.figure()
    plt.imshow(adcs, vmin=-150, vmax=150, aspect='auto', origin='lower')
    plt.xlabel("Channels")
    plt.ylabel("Time tick (512 ns / tick)")
    plt.title(f"50L Run {run_id} Snapshot: {dt_title} -- Trigger ID {trig_id}")
    plt.colorbar()
    plt.savefig(save_path)
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Plot a snapshot from the specified HDF5 file and trigger ID.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument('--record', type=int, help="Trigger Record ID to plot. 0-index", default=0, metavar='n')
    parser.add_argument("--save-all", action="store_true", help="Pass to save snapshots of all trigger IDs")
    parser.add_argument("--tqdm", action="store_true", help="Display tqdm progress bar. Only used for --save-all.")
    parser.add_argument("--savetype", type=str, help="Specify the format to save the figure as. Default: svg.", default="svg")
    parser.add_argument("--subplots", action="store_true", help="Pass to display as 3 subplots for the 3 planes.")
    args = parser.parse_args()

    assert (args.filename[-4:] == "hdf5"), "File name is not an HDF5 data file."
    if (args.record != -1 and args.save_all):
        print("Gave a trigger ID and save-all; saving all.")

    return args

def main():
    args = parse()

    h5_file_name = args.filename
    trig_id = args.record
    save_all = args.save_all
    use_tqdm = args.tqdm
    savetype = args.savetype
    use_subplots = args.subplots

    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

    data = fiftyl_toolkit.Data(h5_file_name)
    records = data.get_records()
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    if save_all:
        for trig_id, record in tqdm(enumerate(records), total=len(records), disable=not use_tqdm, desc="Records"):
            adcs = data.extract(record)
            adcs = median_subtraction(adcs)
            if use_subplots:
                subplot(adcs, run_time, run_id, trig_id, savetype)
            else:
                plot(adcs, run_time, run_id, trig_id, savetype)
        sys.exit(0)

    # Not save_all case
    record = records[trig_id]
    adcs = data.extract(record)
    adcs = median_subtraction(adcs)
##    Coherent noise "removal" test.    ##
#   baseline = np.sum(adcs, axis=1) / 128 # Should be of size (3200,1)
#   print("Baseline shape", baseline.shape)
#   adcs = (adcs.T - baseline).T
    if use_subplots:
        subplot(adcs, run_time, run_id, trig_id, savetype)
    else:
        plot(adcs, run_time, run_id, trig_id, savetype)
    sys.exit(0)

if __name__ == "__main__":
    main()
