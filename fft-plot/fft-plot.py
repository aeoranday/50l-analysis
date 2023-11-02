"""
Plot a single FFT plot for some trigger ID.
"""
import os
import sys
import argparse
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import daqdataformats
import fddetdataformats
from hdf5libs import HDF5RawDataFile
from rawdatautils.unpack.wibeth import np_array_adc

__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

DT_FORMAT = "%Y%m%dT%H%M%S" # datetime format from hdf5 files.
FIGURE_PATH = "./figures"

FRAMES_PER_RECORD = 2240
TOTAL_CHANNELS = 128
CHANNELS_PER_WIB = 64

CH_MAP = [112, 113, 115, 116, 118, 119, 120, 121, 123, 124, 126, 127, 64, 65, 67, 68, 70, 71, 72, 73, 75, 76, 78, 79, 48, 49, 51, 52, 54, 55, 56, 57, 59, 60, 62, 63, 0, 1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 50, 53, 58, 61, 2, 5, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 114, 117, 122, 125, 66, 69, 74, 77]

def pedsub(adcs):
    """
    Pedestal subtract the ADCs.
    """
    return (adcs.T - np.floor(np.median(adcs, axis=1))).T.astype('int')

def extract_adcs(h5_file, record):
    wib_geo_ids = h5_file.get_geo_ids(record)
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

def fft_plot(fft, dt_title, ch_num):
    """
    Plot the FFT plot for the given adc.
    """
    plt.figure()
    freq = np.fft.rfftfreq(FRAMES_PER_RECORD, d=512e-9)
    plt.plot(freq[1:], fft[1:].real, 'k')
    #plt.xlim((0,1e6))
    plt.yscale('symlog')
    plt.xlabel("FFT Frequency (Hz)")
    plt.title("Channel {}-{} Sum FFT: {}".format(ch_num, ch_num+10, str(dt_title)))
    plt.savefig(os.path.join(FIGURE_PATH, "fft{}_{}.svg".format(ch_num, dt_title.strftime(DT_FORMAT))))
    plt.close()

def parse():
    parser = argparse.ArgumentParser(description="Plot the channel FFT for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("-c", type=int, help="Channel number to start sum from. Default: 24", default=24)
    return parser.parse_args()

def main():
    args = parse()

    if not os.path.isdir("figures"):
        print("Saving figures to ./figures.")
        os.makedirs("figures")

    h5_file_name = args.filename
    ch_num = args.c

    h5_file = HDF5RawDataFile(h5_file_name)
    records = h5_file.get_all_record_ids()
    run_time = datetime.strptime(h5_file_name.split("_")[-1].split(".")[0], DT_FORMAT)

    fft_sum = np.zeros((FRAMES_PER_RECORD // 2 + 1,))
    for record in records:
        adcs = extract_adcs(h5_file, record)

        for idx in range(ch_num, ch_num+10):
            fft = np.fft.rfft(adcs[idx,:])
            fft_sum += np.abs(fft.real)

    fft_plot(fft_sum / len(records), run_time, ch_num)
    sys.exit(0)

if __name__ == "__main__":
    main()
