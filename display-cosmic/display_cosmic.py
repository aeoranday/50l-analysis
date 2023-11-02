"""
Plot a single cosmic event.
"""
import os
import sys
import argparse
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import daqdataformats
import detdataformats
import detchannelmaps
import fddetdataformats
from hdf5libs import HDF5RawDataFile
from rawdatautils.unpack.wibeth import np_array_adc

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

FRAMES_PER_RECORD = 2240
#FRAMES_PER_RECORD = 8256 # Full size of a record
TOTAL_CHANNELS = 128
CHANNELS_PER_WIB = 64

HIT_THRESHOLD = 50 # 150
CHANNEL_THRESHOLD = 20 # 30

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "./figures/kinks"

CH_MAP = [112, 113, 115, 116, 118, 119, 120, 121, 123, 124, 126, 127, 64, 65, 67, 68, 70, 71, 72, 73, 75, 76, 78, 79, 48, 49, 51, 52, 54, 55, 56, 57, 59, 60, 62, 63, 0, 1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 50, 53, 58, 61, 2, 5, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 114, 117, 122, 125, 66, 69, 74, 77]

def ped_sub(adcs):
    """
    Pedestal subtract the ADCs.
    """
    return (adcs.T - np.floor(np.median(adcs, axis=1))).T.astype('int')

def check_cosmic(h5_file, record, hit_threshold = HIT_THRESHOLD, channel_threshold = CHANNEL_THRESHOLD):
    """
    Check that this record is within the threshold for a cosmic event.
        h5_file
            File object that contains all the data.
        record
            Record iteration that specifies which trigger record in the file.
        hit_threshold
            Events with pedestal translated adc greather than this threshold is considered a hit.
        channel_threshold
            Events with hit channels greater than this threshold are considered as cosmic events.
    Returns true if this record is a cosmic and false otherwise.
    """
    wib_geo_ids = h5_file.get_geo_ids(record)

    hits = 0
    for gid in wib_geo_ids:
        frag = h5_file.get_frag(record, gid)
        frag_type = frag.get_fragment_type()
        if (frag_type != daqdataformats.FragmentType.kWIBEth):
            continue

        tmp_adc = np_array_adc(frag)
        if tmp_adc.shape[0] < FRAMES_PER_RECORD:
            continue

        for ch in range(CHANNELS_PER_WIB):
            hits += np.max(tmp_adc[:,ch]  -  np.median(tmp_adc[:,ch])) > hit_threshold

    if hits > channel_threshold:
        return True
    return False

def extract_adcs(h5_file, record):
    wib_geo_ids = h5_file.get_geo_ids(record)
    #adcs = np.zeros( (len(wib_geo_ids) * CHANNELS_PER_WIB, FRAMES_PER_RECORD), dtype='int64' )
    adcs = np.zeros( (TOTAL_CHANNELS, FRAMES_PER_RECORD), dtype='int64' )

    for gid in wib_geo_ids:
        frag = h5_file.get_frag(record, gid)
        frag_type = frag.get_fragment_type()
        if (frag_type != daqdataformats.FragmentType.kWIBEth):
            continue

        det_link = 0xffff & (gid >> 48)

        tmp_adc = np_array_adc(frag)
        if tmp_adc.shape[0] < FRAMES_PER_RECORD:
            continue
        tmp_adc = tmp_adc[:FRAMES_PER_RECORD, :]

        for ch in range(CHANNELS_PER_WIB):
            mapped_ch = CH_MAP.index(det_link * 64 + ch)
            adcs[mapped_ch, :] = tmp_adc.T[ch, :]

    return adcs

def plot(adcs, dt_title, trig_id):
    """
    Given :adcs: is in the traditional 50L ADCs plot format and :dt_title: is datetime
    object to be used in the title.
    Also include :non_cosm_count: in the title.
    """
    plt.figure()
    plt.imshow(adcs.T, vmin=-150, vmax=150, aspect='auto', origin='lower')
    plt.xlabel("Channels")
    plt.ylabel("Time tick (512 ns / tick)")
    plt.title("50L Cosmic Event: {} -- Trigger ID {}".format(str(dt_title), trig_id))
    plt.colorbar()
    plt.savefig(os.path.join(FIGURE_PATH, "cosmic_event_TID{}_{}.svg".format(trig_id, dt_title.strftime(DT_FORMAT))))
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Plot an event or all events from the specified HDF5 file.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument('-c', type=int, help="Specify which cosmic event to display, as in the first, second, third, ..., n-th. Default: 1 (first).", default=1, metavar='n')
    parser.add_argument("--save-all", action="store_true", help="Pass to save all cosmic events. Voids -c.")
    parser.add_argument("--tqdm", action="store_true", help="Pass to use the tqdm progress bar. Only used for --save-all.")

    assert (parser.parse_args().filename[-4:] == "hdf5"), "File name is not an HDF5 data file."

    return parser.parse_args()

def main():
    args = parse()

    h5_file_name = args.filename
    cosm_order = args.c
    save_all = args.save_all
    use_tqdm = args.tqdm

    if not os.path.isdir(FIGURE_PATH):
        print(f"Saving figures to {FIGURE_PATH}.")
        os.makedirs(FIGURE_PATH)

    h5_file = HDF5RawDataFile(h5_file_name)
    records = h5_file.get_all_record_ids()
    run_time = datetime.strptime(h5_file_name.split("_")[-1].split(".")[0], DT_FORMAT)

    # Don't consider counting the cosmic triggers, just save all.
    if save_all:
        for trig_id, record in tqdm(enumerate(records), total=len(records),  disable=not use_tqdm, desc="Records"):
            if check_cosmic(h5_file, record):
                adcs = extract_adcs(h5_file, record)
                adcs = ped_sub(adcs)
                plot(adcs, run_time, trig_id)
        sys.exit(0)

    # Do count the cosmic triggers. Only save one.
    trig_cnt = 0
    for trig_id, record in enumerate(records):
        if check_cosmic(h5_file, record):
            trig_cnt += 1
            if trig_cnt == cosm_order:
                adcs = extract_adcs(h5_file, record)
                adcs = ped_sub(adcs)
                plot(adcs, run_time, trig_id)
                sys.exit(0)
    print("Reached end of events without finding the {}-th cosmic.".format(cosm_order))
    sys.exit(1) # Should this case be considered an exit(1)?

if __name__ == "__main__":
    main()
