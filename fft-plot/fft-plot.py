"""
Plot a single FFT plot for some trigger ID.
"""
import os
import argparse
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import fiftyl_toolkit


__author__ = "Alejandro Oranday"
__contact__ = "alejandro@oran.day"

FIGURE_PATH = "./figures"


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


def plot_fft(fft, num_ticks, run_id, file_index, timestamp, ch_num):
    """
    Plot the FFT plot for the given adc.
    """
    freq = np.fft.rfftfreq(2900, d=512e-9)

    plt.figure(figsize=(6, 4), dpi=300)
    plt.plot(freq[1:], fft[1:].real, 'k')
    #plt.xlim((0,1e6))
    plt.yscale('symlog')

    plt.title(f"FFT: Induction Plane\n{run_id:05}.{file_index:04}")
    plt.xlabel("FFT Frequency (Hz)")

    plt.tight_layout()
    plt.savefig(f"fft_{run_id:06}.{file_index:04}.png")
    plt.close()
    return


def parse():
    parser = argparse.ArgumentParser(description="Plot the channel FFT for an event.")
    parser.add_argument("filename", help="Absolute path of the file to process.")
    parser.add_argument("-c", type=int, help="Channel number to start sum from. Default: 24", default=24)
    parser.add_argument("--map-name", type=str, help="Channel map name to use.")
    return parser.parse_args()


def main():
    args = parse()

    if not os.path.isdir("figures"):
        print("Saving figures to ./figures.")
        os.makedirs("figures")

    h5_file_name = args.filename
    ch_num = args.c
    map_name = args.map_name

    reader = fiftyl_toolkit.WIBEthReader(h5_file_name, map_name)
    records = reader.records
    run_time = reader.creation_timestamp
    run_id = reader.run_id
    file_index = reader.file_index

    fft_sum = None#np.zeros((FRAMES_PER_RECORD // 2 + 1,))
    for record in records:
        adcs = reader.read_record(record)

        for idx in range(10, 50):
            fft = np.fft.rfft(adcs[:2900, idx])
            if fft_sum is None:
                fft_sum = np.abs(fft.real)
            else:
                fft_sum += np.abs(fft.real)
    num_ticks = adcs.shape[0]

    plot_fft(fft_sum / len(records), num_ticks, run_id, file_index, run_time, ch_num)
    return


if __name__ == "__main__":
    main()
