"""
Plot a single snapshot (may contain nothing of note).
"""
import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import fiftyl_toolkit


__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"


FIGURE_PATH = "./figures"

AMPLITUDE_MAX = 800


def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')


def subplot(adcs, timestamp, run_id, file_index, trig_id, savetype):
    """
    Plot 3-pane ADCs for each of the 3 planes.
        adcs
            2D array of ADCs to be plotted.
        timestamp
            Epoch timestamp for when the file was created.
        run_id
            Run ID of the data file.
        file_index
            File index for this data file.
        trig_id
            Trigger ID; used in the plot title.
        savetype
            Image format to save as.
    """
    savename = f"50l-subplots-display_{run_id:04}.{file_index:04}-{trig_id:04}.{savetype}"
    save_path = os.path.join(FIGURE_PATH, savename)

    plane_channels = (("Collection", np.arange(0, 48)),
                    ("Induction 1", np.arange(48, 88)),
                    ("Induction 2", np.arange(88, 128)))

    f, ax = plt.subplots(1,3, sharey=True)
    plt.suptitle(f"50L Event Display {run_id}.{file_index}-{trig_id}:\nTimestamp {timestamp}")
    for idx, (plane, channels) in enumerate(plane_channels):
        z_plot = ax[idx].imshow(adcs[:, channels], origin='lower')
        ax[idx].set_title(plane)
        plt.colorbar(z_plot, ax=ax[idx])
        ax[idx].set_aspect(len(channels) / FRAMES_PER_RECORD)
    f.supxlabel("Channel")
    f.supylabel("Time (512 ns / tick)")
    f.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return


def plot(adcs, timestamp, run_id, file_index, trig_id, savetype):
    """
    Plot ADCs in the traditional 50L heatmap plot format.
        adcs
            2D array of ADCs to be plotted.
        timestamp
            Epoch timestamp for when the file was created.
        run_id
            Run ID of the data file.
        file_index
            File index for this data file.
        trig_id
            Trigger ID; used in the plot title.
        savetype
            Image format to save as.
    """
    savename = f"50l-display_{run_id:04}.{file_index:04}-{trig_id}.{savetype}"
    save_path = os.path.join(FIGURE_PATH, savename)

    plt.figure(figsize=(6, 4), dpi=300)

    plt.imshow(adcs[:250, :], vmin=-AMPLITUDE_MAX, vmax=AMPLITUDE_MAX, aspect='auto')#, interpolation='none')

    plt.title(f"50L Event Display {run_id}.{file_index}-{trig_id}:\nTimestamp {timestamp}")
    plt.xlabel("Channel")
    plt.ylabel("Time (512 ns / tick)")

    plt.colorbar()

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return


def parse():
    parser = argparse.ArgumentParser(description="Plot an event display from the specified HDF5 file and trigger ID.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument('--record', type=int, help="TriggerRecord to plot. 0-index", default=0, metavar='n')
    parser.add_argument("--save-all", action="store_true", help="Pass to save snapshots of all trigger IDs")
    parser.add_argument("--tqdm", action="store_true", help="Display tqdm progress bar. Only used for --save-all.")
    parser.add_argument("--savetype", type=str, help="Specify the format to save the figure as. Default: svg.", default="svg")
    parser.add_argument("--subplots", action="store_true", help="Pass to display as 3 subplots for the 3 planes.")
    parser.add_argument("--map-name", type=str, help="Channel map name to use.")
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
    map_name = args.map_name

    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

    data = fiftyl_toolkit.WIBEthReader(h5_file_name, map_name)
    records = data.records
    run_time = data.creation_timestamp
    run_id = data.run_id
    file_index = data.file_index

    if save_all:
        for trig_id, record in tqdm(enumerate(records), total=len(records), disable=not use_tqdm, desc="Records"):
            adcs = data.read_record(record)
            adcs = median_subtraction(adcs)
            if use_subplots:
                subplot(adcs, run_time, run_id, trig_id, savetype)
            else:
                plot(adcs, run_time, run_id, file_index, trig_id, savetype)
        return

    # Not save_all case
    record = records[trig_id]
    adcs = data.read_record(record)
    adcs = median_subtraction(adcs)
##    Coherent noise "removal" test.    ##
#   baseline = np.sum(adcs, axis=1) / 128 # Should be of size (3200,1)
#   print("Baseline shape", baseline.shape)
#   adcs = (adcs.T - baseline).T
    if use_subplots:
        subplot(adcs, run_time, run_id, trig_id, savetype)
    else:
        plot(adcs, run_time, run_id, file_index, trig_id, savetype)
    return


if __name__ == "__main__":
    main()
