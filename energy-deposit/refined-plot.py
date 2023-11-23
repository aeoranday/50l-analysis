"""
Replot of data from charge_collected.py
"""
import os
import argparse

import numpy as np
import matplotlib.pyplot as plt

SAVE_PATH = "."
OFF_CHANNEL = 20
ON_CHANNEL = 24
BINS = np.arange(0, 5001, 50)

## Solid Angle Ratio: https://vixra.org/pdf/2001.0603v2.pdf
def O(a, b, d):
    alpha = a / (2*d)
    beta = b / (2*d)
    return 4 * np.arctan( alpha * beta / np.sqrt(1 + np.power(alpha, 2) + np.power(beta, 2)) )

## Operations are symmetric to x and y, so a,b and A,B are chosen arbitrarily.
a = 0.5 # cm. Width of a channel.
b = 33 # cm. Length of a channel.
d = 52 # cm. Vertical drift from source to collection plane.

A = 2 # cm. Position offset of center of channel.
B = 0 # cm. Position offset of center of channel.

def load(filename):
    with open(filename, 'rb') as f:
        d = np.load(f)
    low_areas = d[0, :]
    center_areas = d[1, :]
    high_areas = d[2, :]
    total_areas = d[3, :]
    return low_areas, center_areas, high_areas, total_areas

def process_files():
    """
    Take in a list of files and group the histograms appropriately.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    off_center_count = np.zeros((len(BINS)-1))
    off_total_count = np.zeros((len(BINS)-1))
    on_center_count = np.zeros((len(BINS)-1))
    on_total_count = np.zeros((len(BINS)-1))

    for file in args.files:
        _, center_areas, _, total_areas = load(os.path.join(SAVE_PATH, file))
        center_count, _ = np.histogram(center_areas, bins=BINS)
        total_count, _ = np.histogram(total_areas, bins=BINS)
        if str(ON_CHANNEL) in file:
            on_center_count += center_count
            on_total_count += total_count
        else:
            off_center_count += center_count
            off_total_count += total_count
    return off_center_count, off_total_count, on_center_count, on_total_count

def main():
    off_center_count, off_total_count, on_center_count, on_total_count = process_files()

    ## Solid Angle Adjustment
    center_solid_angle = O(a, b, d)
    off_center_solid_angle = ( O(2*(A + a), 2*(B+b), d)
                              -O(2*A, 2*(B + b), d)
                              -O(2*(A + a), 2*B, d)
                              +O(2*A, 2*B, d) ) / 4
    #solid_angle_ratio = center_solid_angle / off_center_solid_angle
    solid_angle_ratio = 1

    # Increasing according to solid angle ratio from the center channel
    off_center_count = solid_angle_ratio * off_center_count.astype('float64')
    off_total_count = solid_angle_ratio * off_total_count.astype('float64')

    reduced_center = on_center_count - off_center_count
    reduced_total = on_total_count - 1.0*off_total_count

    ## Plotting
    plt.figure(figsize=(6,4))
    plt.title(f"Reduced Off Center ADC Integral")
#    plt.stairs(off_total_count, BINS, color='#EE442F', alpha=0.6, fill=True, label=f"Off Center Channel Count : {np.sum(off_total_count)}")
    plt.stairs(reduced_total, BINS, color='#63ACBE', alpha=0.6, fill=True, label=f"Reduced Center Channel Count : {np.sum(reduced_total)}")
    #plt.hist(center_areas, bins=BINS, color='#EE442F', alpha=0.6, label=f"Channel {CHANNEL}")
    #plt.hist(total_areas, bins=BINS, color='#63ACBE', alpha=0.6, label=f"Channel {CHANNEL}±1")
    plt.xlabel(f"ADC Area (Bin Width = {BINS[1] - BINS[0]})")
    plt.ylim((0, 300))
    plt.yticks(np.arange(0, 301, 50))
    plt.legend()
    plt.tight_layout()
    plt.savefig("multiple_off_center_reduction.svg")
    plt.close()

if __name__ == "__main__":
    main()
