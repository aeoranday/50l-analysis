# Display Cosmics
Create a heatmap from 50L ADC value (z), channels (x), and time (y). Uses a naive thresholding to classify cosmics that should be revised.

```
$ python display_cosmic.py --help
usage: display_cosmic.py [-h] [-c n] [--save-all] [--tqdm] filename

Plot an event or all events from the specified HDF5 file.

positional arguments:
  filename    Absolute path of file to process. Must be an HDF5 data file.

options:
  -h, --help  show this help message and exit
  -c n        Specify which cosmic event to display, as in the first, second, third, ..., n-th. Default: 1 (first).
  --save-all  Pass to save all cosmic events. Voids -c.
  --tqdm      Pass to use the tqdm progress bar. Only used for --save-all.
```
