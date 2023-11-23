# Bi207 Energy Deposition WIP
Count the ADC area for peaks that are above a threshold on the collection plane for a given channel and adjacent channels. If multiple channels are above threshold, consider this as a muon and discard. Use `--induction` to use coincidence in the induction planes for an additional cut (hard coded position for 2023.11.23 Bi207).

Plot the result for the central channel, each adjacent channel, and the sum of the three histograms separately. Save a `np.ndarray` that contains the result for all four histograms so that they may be replotted later.
```
$ python charge_collected.py --help
usage: charge_collected.py [-h] [--savetype SAVETYPE] [--channel CHANNEL] [--tqdm] [--induction] filename

Calculate the area under peaks and plot in a histogram.

positional arguments:
  filename             Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help           show this help message and exit
  --savetype SAVETYPE  File type to save the figure as. Default : svg.
  --channel CHANNEL    Channel to operate the calculation on . Default = 24.
  --tqdm               Use tqdm to display progress.
  --induction          Use coincidence with induction planes to cut data.
```

`refined-plot.py` is an included plotting script that uses processed histograms that were saved in `saved_arrays` (or deeper).

Structure of code is current WIP and can be heavily refined and improved.
