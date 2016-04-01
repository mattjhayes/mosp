# mosp
## Measure Operating System Performance (mosp)

This code measures operating system performance,
including CPU, memory, disk and network, and
outputs stats to screen and optionally to file
too, for use in performance analysis

Uses the python **psutil** library

## Install

Install psutil (Ubuntu-specific) if you don't already have it:
```
sudo apt-get install python-dev
sudo pip install psutil
```

## Usage
```
python mosp.py [options]
```

#### Options
``` -h  --help```          Display this help and exit

``` -m  --max-run-time```  Maximum time to run for before exiting
                           (default is infinite)

```-i  --interval```       Interval between requests in seconds
                           (default is 1)

```-w  --output-file```    Specify an output filename

```-W```                   Output results to default filename

default format is: *mosp-HOSTNAME-YYYYMMDD-HHMMSS.csv*

```-b  --output-path```         Specify path to output file directory

```-j  --no-header-row```       Suppress writing header row into CSV

```-v  --version```       Output version information and exit

Results are written in following CSV format:
```<timestamp>,<FOO>,<elapsed_time>```

### Example
```
python mosp.py -W -i 2
```
