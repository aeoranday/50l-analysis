# ADC Extrema Histograms
Create histograms based on the ADC extrema. On low activity records, the extrema are likely to be caused by noise, but on cosmic activity, this makes use of the bipolar signal in the 50 L induction planes to search the extrema: by assuming the maximum correctly identifies the cosmic activity, the minimum should occur within a short window afterwards and limits the minima search to that window.

```
$ python adc_extrema_histogram.py --help
usage: adc_histogram.py [-h] [--savetype SAVETYPE] [--channel CHANNEL] filename

Plot a histogram of ADC count extrema.

positional arguments:
  filename             Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help           show this help message and exit
  --savetype SAVETYPE  Specify the format to save the figure as. Default: svg.
  --channel CHANNEL    Specify which channel to generate the histogram from.
```
