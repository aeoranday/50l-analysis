"""
For charges on a channel, calculate the integral
for ADC peaks.
"""
import os
import sys
import argparse
import datetime

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "./figures/bin-50/induction"
SAVE_PATH = "./saved_arrays/threshold-100/induction"

BINS = np.arange(0, 5001, 50)
PREFIX = 5
SUFFIX = 5
THRESHOLD = 100
INDUCTION_THRESHOLD = 40
INDUCTION1_CENTER = 68
INDUCTION2_CENTER = 108
INDUCTION_WINDOW = 15

def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def check_muon(wfs):
    """
    If all three channels are active, call it a muon.
    """
    return np.all(wfs > THRESHOLD)

def check_induction(ind1_wfs, ind2_wfs, time):
    """
    If the center induction channels are above threshold, return True.
    Requires a time shift compared to collection.
    """
    early_time = time - INDUCTION_WINDOW
    if early_time < 0:
        early_time = 0

    ind1_window = ind1_wfs[early_time:time+1]
    ind2_window = ind2_wfs[early_time:time+1]
    return np.max(ind1_window) > INDUCTION_THRESHOLD and -1*np.min(ind2_window) > INDUCTION_THRESHOLD

def parse():
    parser = argparse.ArgumentParser(description="Calculate the area under peaks and plot in a histogram.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument("--savetype", type=str, help="File type to save the figure as. Default : svg.", default="svg")
    parser.add_argument("--channel", type=int, help="Channel to operate the calculation on . Default = 24.", default=24)
    parser.add_argument("--tqdm", action="store_true", help="Use tqdm to display progress.")
    parser.add_argument("--induction", action="store_true", help="Use coincidence with induction planes to cut data.")

    return parser.parse_args()

def mkdirs(path):
    """
    Check if the save dirs are made. If not, make them.
    """
    if not os.path.isdir(path):
        print(f"Saving figures to {path}.")
        os.makedirs(path)

def save(data, channel, run_id, sub_run_id):
    """
    Save data to a numpy file.
    """
    savename = f"adc-integral_channel-{channel}_run-{run_id}.{sub_run_id}.npy"
    savepath = os.path.join(SAVE_PATH, savename)
    with open(savepath, 'wb') as f:
        np.save(f, data)

def plot_all(areas, channel, num_events, run_time, run_id, savetype):
    """
    Plot a histogram of the ADC areas including adjacent channels.
    """
    savename = f"adj-adc-integral_channel-{channel}_run-{run_id}_{run_time.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    count, _ = np.histogram(areas, bins=BINS)
    num_hist = np.sum(count)

    plt.figure(figsize=(6,4))
    plt.title(f"ADC Integral: Channel {channel}±1\n Total Count: {num_hist} Run {run_id} : {run_time}")
    plt.hist(areas, bins=BINS, color='k')
    plt.xlabel(f"ADC Area (Bin Width = {BINS[1] - BINS[0]})")
    plt.ylim((0, 125))
    plt.yticks(np.arange(0,126,25))
    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()

def plot(areas, channel, num_events, run_time, run_id, savetype):
    """
    Plot a histogram of the ADC areas.
    """
    savename = f"adc-integral_channel-{channel}_run-{run_id}_{run_time.strftime(DT_FORMAT)}.{savetype}"
    savepath = os.path.join(FIGURE_PATH, savename)

    count, _ = np.histogram(areas, bins=BINS)
    num_hist = np.sum(count)

    plt.figure(figsize=(6,4))
    plt.title(f"ADC Integral: Channel {channel}\n Total Count: {num_hist} Run {run_id} : {run_time}")
    plt.hist(areas, bins=BINS, color='k')
    plt.xlabel(f"ADC Area (Bin Width = {BINS[1] - BINS[0]})")
    plt.ylim((0, 125))
    plt.yticks(np.arange(0, 126, 25))
    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()

def main():
    ### Process Arguments
    args = parse()

    filename = args.filename
    savetype = args.savetype
    channel = args.channel
    use_tqdm = args.tqdm
    induction = args.induction

    mkdirs(FIGURE_PATH)
    mkdirs(SAVE_PATH)

    ### Extract Data
    data = fiftyl_toolkit.Data(filename)
    records = data.get_records()
    run_time = data.get_datetime()
    run_id = data.get_run_id()
    sub_run_id = data.get_sub_run_id()

    ### Processing & Plotting

    adc_threshold = THRESHOLD
    prefix = PREFIX
    suffix = SUFFIX

    mismatch = 0
    muon_count = 0
    induction_skip = 0

    low_areas = []
    center_areas = []
    high_areas = []
    total_areas = []

    for record in tqdm(records, total=len(records), desc="Records", disable=not use_tqdm):
        try:
            wfs = data.extract(record, [channel-1, channel, channel+1])
            wfs = median_subtraction(wfs) # (num_frames, num_channels)

            if induction:
                ind1_wfs = data.extract(record, [INDUCTION1_CENTER-1, INDUCTION1_CENTER, INDUCTION1_CENTER+1])
                ind1_wfs = median_subtraction(ind1_wfs)

                ind2_wfs = data.extract(record, [INDUCTION2_CENTER-1, INDUCTION2_CENTER, INDUCTION2_CENTER+1])
                ind2_wfs = median_subtraction(ind2_wfs)

            low_sum = 0
            center_sum = 0
            high_sum = 0
            total_sum = 0

            for time in range(wfs.shape[0]):
                if check_muon(wfs[time, :]):
                    muon_count += 1
                    continue
                if wfs[time, 1] > adc_threshold:
                    ## Start New Window Case
                    if center_sum == 0:
                        if time < prefix:
                            prefix = time

                        low_sum += np.sum(wfs[time-prefix:time+1, 0])
                        center_sum += np.sum(wfs[time-prefix:time+1, 1])
                        high_sum += np.sum(wfs[time-prefix:time+1, 2])
                        total_sum += np.sum(wfs[time-prefix:time+1, :])

                        prefix = PREFIX
                    else: ## Continue Window Case
                        low_sum += wfs[time, 0]
                        center_sum += wfs[time, 1]
                        high_sum += wfs[time, 2]
                        total_sum += np.sum(wfs[time,:])
                elif center_sum != 0: ## End Window Case
                    if induction: # Use induction coincidence.
                        if check_induction(ind1_wfs, ind2_wfs, time):
                            if wfs.shape[0] < time+suffix:
                                suffix = wfs.shape[0] - time

                            low_sum += np.sum(wfs[time:time+suffix, 0])
                            center_sum += np.sum(wfs[time:time+suffix, 1])
                            high_sum += np.sum(wfs[time:time+suffix, 2])
                            total_sum += np.sum(wfs[time:time+suffix, :])

                            suffix = SUFFIX

                            low_areas.append(low_sum)
                            center_areas.append(center_sum)
                            high_areas.append(high_sum)
                            total_areas.append(total_sum)
                        else:
                            induction_skip += 1
                    else: # Same effect, but don't check induction coincidence.
                        if wfs.shape[0] < time+suffix:
                            suffix = wfs.shape[0] - time

                        low_sum += np.sum(wfs[time:time+suffix, 0])
                        center_sum += np.sum(wfs[time:time+suffix, 1])
                        high_sum += np.sum(wfs[time:time+suffix, 2])
                        total_sum += np.sum(wfs[time:time+suffix, :])

                        suffix = SUFFIX

                        low_areas.append(low_sum)
                        center_areas.append(center_sum)
                        high_areas.append(high_sum)
                        total_areas.append(total_sum)

                    ## Reset
                    low_sum = 0
                    center_sum = 0
                    high_sum = 0
                    total_sum = 0
        except ValueError:
            mismatch += 1

    print("#### Sums ####")
    print("Low Area Sum:", np.sum(low_areas))
    print("Center Area Sum:", np.sum(center_areas))
    print("High Area Sum:", np.sum(high_areas))
    print("Total Area Sum:", np.sum(total_areas))
    print("")

    print("#### Rejects ####")
    print("Total mismatch:", mismatch)
    print("Identified muons:", muon_count)
    print("Induction skips:", induction_skip)
    print("")

    print("#### Counts ####")
    counts, _ = np.histogram(center_areas, bins=BINS)
    print("Histogram Count:", np.sum(counts))

    num_events = len(records) - mismatch
    print("Total Events:", num_events)

    plot(low_areas, channel-1, num_events, run_time, run_id, savetype)
    plot(center_areas, channel, num_events, run_time, run_id, savetype)
    plot(high_areas, channel+1, num_events, run_time, run_id, savetype)

    plot_all(total_areas, channel, num_events, run_time, run_id, savetype)

    np_areas = np.array([low_areas, center_areas, high_areas, total_areas])
    save(np_areas, channel, run_id, sub_run_id)

if __name__ == "__main__":
    main()
