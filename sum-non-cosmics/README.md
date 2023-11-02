# Sum Threshold
Set array values outside of threshold bounds to zero and sum for each event. Waveforms are median subtracted then thresholded.

Colorbar is not set to the best configuration. This is because each data file ends with very different coloring values. For this reason, the processed array is saved to `saved_arrays` with the intention to replot later interactively.

This script still uses the legacy code before `fiftyl_toolkit` module was made. It can be translated, but I have yet to take the time to do so.

```
$ python sum_threshold.py --help
usage: sum_threshold.py [-h] [--tqdm] [--abs] [--subplots] filename

Zero values outside of threshold and sum events, plot the resulting heatmap, and save this array.

positional arguments:
  filename    Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help  show this help message and exit
  --tqdm      Use to display tqdm progress bar. Default off.
  --abs       Use to sum using absolute value.
  --subplots  Use to display as subplots.
```

## Examples
```
python sum_threshold.py /path/to/file.hdf5 --abs
python sum_threshold.py /path/to/file.hdf5 --tqdm

python sum_threshold.py ~/50l_setup/configs/test/50l_run000208_0000_dataflow0_datawriter_0_20231016T131047.hdf5
```
