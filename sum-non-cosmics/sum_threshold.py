"""
Zero channels outside of threshold and sum all events in a given file, plot the resulting heatmap, and save the array.
"""
import os
import sys
import argparse
import datetime

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
TOTAL_CHANNELS = 128
CHANNELS_PER_WIB = 64

LOW_THRESHOLD = 63 # 95
HIGH_THRESHOLD = 77 # 150

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.

FIGURE_PATH = "figures/zero_events"
SAVE_PATH = "saved_arrays/zero_events"

CH_MAP = [112, 113, 115, 116, 118, 119, 120, 121, 123, 124, 126, 127, 64, 65, 67, 68, 70, 71, 72, 73, 75, 76, 78, 79, 48, 49, 51, 52, 54, 55, 56, 57, 59, 60, 62, 63, 0, 1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 50, 53, 58, 61, 2, 5, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 114, 117, 122, 125, 66, 69, 74, 77]

def pedsub(adcs):
    """
    Pedestal subtract given ADCs.
    """
    return (adcs.T - np.floor(np.median(adcs, axis=1))).T.astype('int')

def extract_adcs(h5_file, record):
    wib_geo_ids = h5_file.get_geo_ids(record)
    adcs = np.zeros( (len(wib_geo_ids) * CHANNELS_PER_WIB, FRAMES_PER_RECORD), dtype='int64' )

    for i, gid in enumerate(wib_geo_ids):
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

def zero_sum_events(h5_file, records, use_tqdm=False, use_abs=False):
    """
    Zero all values outside of the range [LOW_THRESHOLD, HIGH_THRESHOLD] and sum these events.
        h5_file
            Data object to view events from.
        records
            List of record IDs to view.
        use_tqdm
            If True, display the tqdm progress bar.
        use_abs
            If True, use absolute values during the summation.
    """
    summed_events = np.zeros( (TOTAL_CHANNELS, FRAMES_PER_RECORD), dtype='int64' )
    event_count = 0

    sum_operator = lambda x: x # Do not transform the value.
    if use_abs:
        sum_operator = np.abs # Transform by absolute value

    for idx, record in tqdm(enumerate(records), desc="Record", total=len(records), disable=not use_tqdm):
        wib_geo_ids = h5_file.get_geo_ids(record)
        
        for gid in wib_geo_ids:
            frag = h5_file.get_frag(record, gid)
            frag_type = frag.get_fragment_type()
            if (frag_type != daqdataformats.FragmentType.kWIBEth):
                continue

            tmp_adc = np_array_adc(frag)
            if tmp_adc.shape[0] < FRAMES_PER_RECORD:
                continue

        event_count += 1
        adcs = extract_adcs(h5_file, record)
        adcs = pedsub(adcs)
        adcs_mask = (LOW_THRESHOLD >= adcs) | (adcs >= HIGH_THRESHOLD)
        #adcs_mask[:88,:] = False
        #adcs[adcs_mask] = 0
        summed_events += sum_operator(adcs)

    print("Total events:", event_count)
    return summed_events, event_count

def subplot(adcs, dt_title, run_id, event_count, use_abs=False):
    """
    Plot 3-pane summed ADCs for each of the 3 planes.
        adcs
            2D array of ADCs to be plotted.
        dt_title
            datetime format from the data file; used in the plot title.
        run_id
            Run ID number. (Multiple data files may have the same run ID.)
        event_count
            Number of events that were summed for this plot; used in the plot title.
        use_abs
            Boolean if absolute value was used; used in the plot title.
    """
    savename = f"semi-filtered_summed_zero_events_subplots_{dt_title.strftime(DT_FORMAT)}.svg"
    if use_abs:
        savename = "abs_" + savename

    savepath = os.path.join(FIGURE_PATH, savename)

    plane_channels = (("Collection", np.arange(0, 48)),
                    ("Induction 1", np.arange(48, 88)),
                    ("Induction 2", np.arange(88, 128)))

    f, ax = plt.subplots(1,3, sharey=True)
    if use_abs:
        plt.suptitle(f"50L {run_id} Absolute Summed Non-Cosmics\n{str(dt_title)} -- {event_count} Events")
    else:
        plt.suptitle(f"50L {run_id} Summed Non-Cosmics\n{str(dt_title)} -- {event_count} Events")
    for idx, (plane, channels) in enumerate(plane_channels):
        z_plot = ax[idx].imshow(adcs.T[:, channels], aspect='auto', origin='lower')
        ax[idx].set_title(plane)
        plt.colorbar(z_plot, ax=ax[idx])
    f.supxlabel("Channels")
    f.supylabel("Time tick (512 ns / tick)")
    f.tight_layout()
    plt.savefig(savepath)
    plt.close()

def plot(adcs, dt_title, run_id, event_count, use_abs=False):
    """
    Plot summed ADCs in the traditional 50L heatmap format.
        adcs
            2D array of ADCs to be plotted.
        dt_title
            datetime format from the data file; used in the plot title.
        run_id
            Run ID number. (Multiple data files may have the same run ID.)
        event_count
            Number of events that were summed for this plot; used in the plot title.
        use_abs
            Boolean if absolute value was used; used in the plot title.
    """
    savename = f"summed_zero_events_{dt_title.strftime(DT_FORMAT)}.svg"
    if use_abs:
        savename = "abs_" + savename

    savepath = os.path.join(FIGURE_PATH, savename)

    plt.figure()
    #plt.imshow(adcs.T, vmin=-2000, vmax=2000, aspect='auto')
    plt.imshow(adcs.T, vmin=0, vmax=200, aspect='auto') # Doing vmin/vmax parameter testing. Oct-19-2023.
    plt.xlabel("Channels")
    plt.ylabel("Time tick (512 ns / tick)")

    if use_abs:
        plt.title(f"50L {run_id} Absolute Summed Non-Cosmics\n{str(dt_title)} -- {event_count} Events")
    else:
        plt.title(f"50L {run_id} Summed Non-Cosmics\n{str(dt_title)} -- {event_count} Events")
    plt.colorbar()
    if use_abs:
        plt.savefig(savepath)
    else:
        plt.savefig(savepath)
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Zero values outside of threshold and sum events, plot the resulting heatmap, and save this array.")
    parser.add_argument("filename", help="Absolute path of file to process. Must be an HDF5 data file.")
    parser.add_argument("--tqdm", action="store_true", help="Use to display tqdm progress bar. Default off.")
    parser.add_argument("--abs", action="store_true", help="Use to sum using absolute value.")
    parser.add_argument("--subplots", action="store_true", help="Use to display as subplots.")
    args = parser.parse_args()

    assert (args.filename[-4:] == "hdf5"), "File name is not an HDF5 data file."
    return args

def main():
    args = parse()

    h5_file_name = args.filename
    use_tqdm = args.tqdm
    use_abs = args.abs
    use_subplots = args.subplots

    # Check if the save dirs are made. If not, make them.
    if not os.path.isdir("figures/zero_events"):
        print("Saving figures to ./figures/zero_events.")
        os.makedirs("figures/zero_events")
    if not os.path.isdir("saved_arrays/zero_events"):
        print("Saving numpy arrays to ./saved_arrays/zero_events.")
        os.makedirs("saved_arrays/zero_events")

    # Data file names are in the format
    # *_YYYYmmddTHHMMSS.hdf5 -> double split and DT_FORMAT to extract
    run_time = datetime.datetime.strptime(h5_file_name.split('_')[-1].split('.')[0],
                                          DT_FORMAT)
    run_id = int(h5_file_name.split('/')[-1].split('_')[1][3:])

    h5_file = HDF5RawDataFile(h5_file_name)
    records = h5_file.get_all_record_ids()

    summed_events, event_count = zero_sum_events(h5_file, records, use_tqdm, use_abs)

    if use_abs:
        with open("./saved_arrays/zero_events/semi-filtered_abs_summed_zero_events_{}.npy".format(run_time.strftime(DT_FORMAT)), "wb") as f:
            np.save(f, summed_events)
    else:
        with open("./saved_arrays/zero_events/semi-filtered_summed_zero_events_{}.npy".format(run_time.strftime(DT_FORMAT)), "wb") as f:
            np.save(f, summed_events)

    if use_subplots:
        subplot(summed_events, run_time, run_id, event_count, use_abs)
    else:
        plot(summed_events, run_time, run_id, event_count, use_abs)
    sys.exit(0)

if __name__ == "__main__":
    main()
