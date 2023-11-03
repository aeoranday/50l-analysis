"""
Sum all events in a given file, plot the resulting heatmap, and save the array.
"""
import os
import sys
import argparse
import datetime

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from tqdm import tqdm

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "./figures"
SAVE_PATH = "./saved_arrays"
CHANNEL = 24

def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def mean_subtraction(adcs):
    """
    Mean subtract the ADCs.
    """
    return (adcs - np.floor(np.mean(adcs, axis=0))).astype('int')

def mode_subtraction(adcs):
    """
    Mode subtract the ADCs.
    """
    mode_array = np.array(stats.mode(adcs)[0])
    return (adcs - mode_array).astype('int')

def plot(adcs, dt_title, event_count, run_id, use_abs=False, savetype="svg"):
    """
    Plot summed ADCs in the traditional 50L heatmap format.
        adcs
            2D array of ADCs to be plotted.
        dt_title
            datetime format from the data file; used in the plot title.
        event_count
            Number of events that were summed for this plot; used in the plot title.
        run_id
            Run ID number.
        use_abs
            Boolean if absolute value was used; used in the plot title.
        savetype
            File format to save as. Default : svg.
    """
    if use_abs:
        savename = f"abs_summed_run-{run_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"
    else:
        savename = f"summed_run-{run_id}_{dt_title.strftime(DT_FORMAT)}.{savetype}"

    save_path = os.path.join(FIGURE_PATH, savename)
    plt.figure()
    plt.imshow(adcs, aspect='auto') #vmin=-2000, vmax=2000, aspect='auto')
    plt.xlabel("Channels")
    plt.ylabel("Time tick (512 ns / tick)")

    if use_abs:
        plt.title(f"50L Run {run_id} Event Absolute Sum: {str(dt_title)} -- {event_count} Events")
    else:
        plt.title(f"50L Run {run_id} Event Sum: {str(dt_title)} -- {event_count} Events")
    plt.colorbar()
    plt.savefig(save_path)
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Sum non-cosmic events, plot the resulting heatmap, and save this array.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument("--tqdm", action="store_true", help="Use to display tqdm progress bar. Default off.")
    parser.add_argument("--abs", action="store_true", help="Use to sum using absolute value.")
    parser.add_argument("--savetype", type=str, help="File type to save the figure as. Default : svg.", default="svg")
    parser.add_argument("--debug", action="store_true", help="Print some debugging information.")
    parser.add_argument("--ped-est", choices=["median", "mean", "mode"], help="Specify which statistical center (mean, median, mode) to use on pedestal subtraction. Default: median.", default="median")

    args = parser.parse_args()

    assert (args.filename[-4:] == "hdf5"), "File name is not an HDF5 data file."
    return args

def save(array, savename):
    """
    Save the given np.ndarray inside SAVE_PATH.
    """
    save_path = os.path.join(SAVE_PATH, savename)
    with open(save_path, "wb") as f:
        np.save(f, array)

def mkdirs():
    """
    Check if the save dirs are made. If not, make them.
    """
    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)
    if not os.path.isdir(SAVE_PATH):
        print(f"Saving numpy arrays to {SAVE_PATH}.")
        os.makedirs(SAVE_PATH)

def debug_runner(data):
    """
    Runs a short section of the intended code, but prints out information.
    Exits after 5 iterations.
    """
    records = data.get_records()
    adcs = np.zeros((3200, 128))
    for record in records[:5]:
        tmp_adcs = data.extract(record)[:3200, 128]
        print("Original ADCs:", tmp_adcs)
        mode_subbed = mode_subtraction(tmp_adcs)
        print("Mode Subtracted:", mode_subbed)
        coherent_baseline = np.sum(mode_subbed, axis=1) / 128 # <- Number of channels
        mode_subbed = (mode_subbed.T - coherent_baseline).T
        print("Coherent Noise Removal:", mode_subbed)
        adcs += tmp_adcs
        print("Sum:", adcs)
        print("="*20)
    sys.exit(0)

def main():
    ### Process Arguments
    args = parse()

    h5_file_name = args.filename
    use_tqdm = args.tqdm
    use_abs = args.abs
    savetype = args.savetype
    debug = args.debug
    ped_est = args.ped_est

    if ped_est == "median":
        ped_subtraction = median_subtraction
    elif ped_est == "mode":
        ped_subtraction = mode_subtraction
    else:
        ped_subtraction = median_subtraction

    if use_abs:
        sum_operator = np.abs
    else:
        sum_operator = lambda x: x

    mkdirs()

    ### Extract Data
    data = fiftyl_toolkit.Data(h5_file_name)
    records = data.get_records()
    run_time = data.get_datetime()
    run_id = data.get_run_id()

    if debug:
        debug_runner(data)

    ### Processing & Plotting
    adcs = np.zeros((3200, 128))
    mismatch = 0
    for record in tqdm(records, total=len(records), desc="Records", disable=not use_tqdm):
        try:
            tmp_adc = data.extract(record)
        except ValueError:
            mismatch += 1
        if tmp_adc.shape[0] >= adcs.shape[0]:
            ped_subbed = ped_subtraction(tmp_adc[:adcs.shape[0], :])
            adcs += sum_operator(ped_subbed)
        else:
            mismatch += 1

    print("Total mismatched:", mismatch)
    num_events = len(records) -  mismatch

    plot(adcs, run_time, num_events, run_id, use_abs, savetype)
    if use_abs:
        savename = f"abs_summed_run-{run_id}_{run_time.strftime(DT_FORMAT)}.npy"
    else:
        savename = f"summed_run-{run_id}_{run_time.strftime(DT_FORMAT)}.npy"
    save(adcs, savename)

if __name__ == "__main__":
    main()
