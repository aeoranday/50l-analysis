"""
Produce the k-dist graph for a given value of k, data file, and trigger ID.
"""

import argparse
import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import fiftyl_toolkit

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # Datetime format consistent with HDF5 files.

FIGURE_PATH = "./figures"
SAVE_PATH = "./saved_arrays"

BINS = np.arange(0, 651, 5)

# Taken visually from thresholding on a random event.
ADC_THRESHOLD = 200
# Should likely be replaced with RMS or the *future* method for Trigger Primitives.

ADJ_MASK = ((1,0),
            (-1,0),
            (0,1),
            (0,-1),
            (-1,1),
            (1,1),
            (-1,-1),
            (1,-1))

def median_subtraction(adcs):
    """
    Median subtract the ADCs.
    """
    return (adcs - np.floor(np.median(adcs, axis=0))).astype('int')

def manhattan_dist(x, y):
    """
    Return manhattan distance from 2-tuple x to 2-tuple y.
    """
    return np.abs(x[0] - y[0]) + np.abs(x[1] - y[1])

def identify_plane(x):
    """
    Identify the plane that data point x is on.
        x
            2-tuple of (channel, tick).
    Returns 0 (collection), 1 (induction 1), or 2 (induction 2).
    """
    if x[0] < 48: return 0
    if x[0] < 88: return 1
    return 2

def k_dist(adcs, k, dt_title, trig_id):
    """
    Given the adcs heatmap, plot the k-dist graph and save the figure.
    Keep calculations in each plane separate.
        adcs
            np.array of shape (num_chns = 128, frames_per_record = 2240)
        k
            Integer for the neighbor number of interest
        dt_title
            Datetime object to be used in the plot title.
        trig_id
            Trigger ID number to be used in the plot title.
    """
    adcs_ped = np.median(adcs, axis=1)
    adcs_ped_sub = (adcs.T - np.floor(adcs_ped)).T.astype('int')

    hit_locations = np.where(adcs_ped_sub > ADC_THRESHOLD)

    k_distance = []
    for x in zip(hit_locations[0], hit_locations[1]):
        dist = []
        x_plane = identify_plane(x)

        # Intentionally counts itself per the neighbor definition of DBSCAN
        # Calculates distance to *all* points.
        for y in zip(hit_locations[0], hit_locations[1]):
            y_plane = identify_plane(y)
            if x_plane == y_plane:
                dist.append(manhattan_dist(x,y))
        dist.sort()
        k_distance.append(dist[k]) # Only keep the distance to the k-th point.

    k_distance = sorted(k_distance, reverse=True)
    plt.figure()
    plt.scatter(range(len(k_distance)), k_distance, s=2, color='k')
    plt.title(f"{k}-dist: {dt_title} Trigger ID{trig_id}")
    plt.xlabel("Points")
    plt.ylabel(f"{k}-dist : Manhattan")
    plt.ylim((0, 600))
    plt.savefig(os.path.join(FIGURE_PATH, f"{k:02}-dist_{dt_title.strftime(DT_FORMAT)}-TID{trig_id}.svg"))

    return k_distance

def histogram(k_distance, k, run_id, sub_run_id, trig_id, savetype):
    """
    Plot the k-distance metric as a histogram.
        k_distance
            Measured k-distance from the function k_dist.
        k
            Integer for the neighbor number of interest.
        dt_title
            Datetime object to be used in the plot title.
        trig_id
            Trigger ID number to be used in the plot title.
    """
    savename = f"{k:02}-dist_histogram_run-{run_id}.{sub_run_id}.{savetype}"
    plt.figure(figsize=(6,4))
    plt.title(f"{k}-dist Histogram: Run {run_id}.{sub_run_id} Record {trig_id}")
    plt.hist(k_distance, bins=BINS, color='k')
    plt.ylabel("Count")
    plt.xlabel(f"Manhattan Distance to k={k} Point")
    plt.ylim((0, 600))
    plt.xlim((-5, 650))
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_PATH, "hist", savename))

def parse():
    parser = argparse.ArgumentParser(description="Plotting k-dist graph for DBSCAN use.")

    parser.add_argument('-t', "--trigger", type=int, help="Specify which Trigger ID to process. Default: 0.", default=0, metavar='trig_id')
    parser.add_argument("filename", help="Name of file to process. Must be an HDF5 data file.")
    parser.add_argument('-k', type=int, help="k value of interest to look at.", required=True, metavar='k')
    parser.add_argument("--savetype", type=str, help="Image type to save as. Default : svg.", default="svg")
    assert (parser.parse_args().filename[-4:] == "hdf5"), "File name is not an HDF5 data file."

    return parser.parse_args()

def main():
    args = parse()

    filename = args.filename
    k = args.k
    trig_id = args.trigger
    savetype = args.savetype

    data = fiftyl_toolkit.Data(filename)
    run_time = data.get_datetime()
    run_id = data.get_run_id()
    subrun_id = data.get_sub_run_id()

    record = data.get_records()[trig_id]
    adcs = data.extract(record)
    adcs = median_subtraction(adcs)
    k_distance = k_dist(adcs, k, run_time, trig_id)
    histogram(k_distance, k, run_id, subrun_id, trig_id, savetype)

    with open(os.path.join(SAVE_PATH, f"{k:02}-dist_{run_time.strftime(DT_FORMAT)}-TID{trig_id}.npy"), 'wb') as f:
        np.save(f, k_distance)

if __name__ == "__main__":
    main()
