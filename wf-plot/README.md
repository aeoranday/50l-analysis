# Waveform Plot
Plot the channel waveform for a given data file and record ID.

```
$ python wf-plot.py --help
usage: wf-plot.py [-h] [--record RECORD] [--channel CHANNEL] [--savetype SAVETYPE] filename

Plot the channel waveform for a record ID.

positional arguments:
  filename             Absolute path of the file to process.

options:
  -h, --help           show this help message and exit
  --record RECORD      Trigger Record ID to plot. Default: 0.
  --channel CHANNEL    Channel number to view. Default: 24.
  --savetype SAVETYPE  Figure save type to use. Default: svg.
```
