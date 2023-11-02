# Sum All
Sum all records within a data file and plot as a heatmap with summed ADC (z), channel (x), and time (y).

```
$ python sum_all.py --help
usage: sum_all.py [-h] [--tqdm] [--abs] [--savetype SAVETYPE] [--debug] filename

Sum non-cosmic events, plot the resulting heatmap, and save this array.

positional arguments:
  filename             Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help           show this help message and exit
  --tqdm               Use to display tqdm progress bar. Default off.
  --abs                Use to sum using absolute value.
  --savetype SAVETYPE  File type to save the figure as. Default : svg.
  --debug              Print some debugging information.
```
