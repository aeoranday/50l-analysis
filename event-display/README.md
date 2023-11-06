# Event display
Create a heatmap from 50L ADC value (z), channels (x), and time (y) from the given data file and trigger record. This does not check the content of the record and may display a heatmap with little to no activity.

```
$ python event_display.py --help
usage: event_display.py [-h] [--record n] [--save-all] [--tqdm] [--savetype SAVETYPE] [--subplots] filename

Plot a snapshot from the specified HDF5 file and trigger ID.

positional arguments:
  filename             Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help           show this help message and exit
  --record n           Trigger Record ID to plot. 0-index
  --save-all           Pass to save snapshots of all trigger IDs
  --tqdm               Display tqdm progress bar. Only used for --save-all.
  --savetype SAVETYPE  Specify the format to save the figure as. Default: svg.
  --subplots           Pass to display as 3 subplots for the 3 planes.
```
