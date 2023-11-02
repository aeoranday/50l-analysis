# RMS Plot
Create the RMS plot for a given data file and trigger record. Optional take the average for all trigger records in the data file.

```
$ python rms-plot.py --help
usage: rms-plot.py [-h] [--tqdm] [--savetype SAVETYPE] [--record RECORD | --avg] filename

Plot the channel RMS for an event.

positional arguments:
  filename             Absolute path of the file to process.

options:
  -h, --help           show this help message and exit
  --tqdm               Display average RMS progress with tqdm.
  --savetype SAVETYPE  Choose filetype to save plot as. Default: svg.
  --record RECORD      Trigger Record ID to plot.
  --avg                Plot the average RMS for all records.
```
