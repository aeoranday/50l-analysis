# Running Sum
Perform a running sum on a given waveform given the data file, trigger record ID, and channel number.

```
$ python running_sum.py --help
usage: running_sum.py [-h] [--savetype SAVETYPE] [--channel CHANNEL] [--record RECORD] [--mini] filename

Sum non-cosmic events, plot the resulting heatmap, and save this array.

positional arguments:
  filename             Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help           show this help message and exit
  --savetype SAVETYPE  File type to save the figure as. Default : svg.
  --channel CHANNEL    Channel to operate the running sum on. Default = 24.
  --record RECORD      Trigger Record ID to operate the running sum on. Default = 0.
  --mini               Include a mini-figure of the original waveform. Default = False.
```

## Example
```
python running_sum.py ~/50l_setup/configs/test/50l_run000250_0000_dataflow0_datawriter_0_20231024T071446.hdf5 --channel 110 --record 5
```
