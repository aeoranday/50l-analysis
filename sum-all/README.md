# Sum All
Sum all records within a data file and plot as a heatmap with summed ADC (z), channel (x), and time (y).

```
$ python sum_all.py --help
usage: sum_all.py [-h] [--tqdm] [--abs] [--savetype SAVETYPE] [--debug] [--ped-est {median,mean,mode}] filename

Sum all events in a dataset and plot as a heatmap.

positional arguments:
  filename              Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help            show this help message and exit
  --tqdm                Use to display tqdm progress bar. Default off.
  --abs                 Use to sum using absolute value.
  --savetype SAVETYPE   File type to save the figure as. Default : svg.
  --debug               Print some debugging information.
  --ped-est {median,mean,mode}
                        Specify which statistical center (mean, median, mode) to use on pedestal subtraction. Default: median.
```

## Examples
```
python sum_all.py /path/to/file.hdf5 --tqdm --ped-est median
python sum_all.py /path/to/file.hdf5

python sum_all.py ~/50l_setup/configs/test/50l_run000208_0000_dataflow0_datawriter_0_20231016T131047.hdf5
```
