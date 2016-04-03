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

### Example
```
python mosp.py -W -i 2
```

### Example KVP output
```
2016-04-03 22:32:53.007 cpu[0]=0.0 swap-in=0 swap-out=0 pkts-in[lo]=0 pkts-out[lo]=0 bytes-in[lo]=0 bytes-out[lo]=0 pkts-in[eth2]=0 pkts-out[eth2]=0 bytes-in[eth2]=0 bytes-out[eth2]=0 pkts-in[eth1]=0 pkts-out[eth1]=0 bytes-in[eth1]=0 bytes-out[eth1]=0 pkts-in[eth0]=0 pkts-out[eth0]=0 bytes-in[eth0]=0 bytes-out[eth0]=0
2016-04-03 22:32:54.009 cpu[0]=23.5 swap-in=0 swap-out=0 pkts-in[lo]=0 pkts-out[lo]=0 bytes-in[lo]=0 bytes-out[lo]=0 pkts-in[eth2]=2 pkts-out[eth2]=2 bytes-in[eth2]=158 bytes-out[eth2]=158 pkts-in[eth1]=0 pkts-out[eth1]=0 bytes-in[eth1]=0 bytes-out[eth1]=0 pkts-in[eth0]=0 pkts-out[eth0]=0 bytes-in[eth0]=0 bytes-out[eth0]=0
2016-04-03 22:32:55.010 cpu[0]=22.7 swap-in=0 swap-out=0 pkts-in[lo]=0 pkts-out[lo]=0 bytes-in[lo]=0 bytes-out[lo]=0 pkts-in[eth2]=1 pkts-out[eth2]=1 bytes-in[eth2]=98 bytes-out[eth2]=98 pkts-in[eth1]=0 pkts-out[eth1]=0 bytes-in[eth1]=0 bytes-out[eth1]=0 pkts-in[eth0]=0 pkts-out[eth0]=0 bytes-in[eth0]=0 bytes-out[eth0]=0
```

### Example CSV output
```
time,ct1-cpu[0],ct1-swap-in,ct1-swap-out,ct1-pkts-in[lo],ct1-pkts-out[lo],ct1-bytes-in[lo],ct1-bytes-out[lo],ct1-pkts-in[eth2],ct1-pkt
s-out[eth2],ct1-bytes-in[eth2],ct1-bytes-out[eth2],ct1-pkts-in[eth1],ct1-pkts-out[eth1],ct1-bytes-in[eth1],ct1-bytes-out[eth1],ct1-pkt
s-in[eth0],ct1-pkts-out[eth0],ct1-bytes-in[eth0],ct1-bytes-out[eth0],
2016-04-03 22:33:54.669,0.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
2016-04-03 22:33:55.671,19.4,0,0,0,0,0,0,1,1,98,98,0,0,0,0,0,0,0,0,
2016-04-03 22:33:56.674,31.0,0,0,0,0,0,0,1,1,98,98,1,1,74,60,0,0,0,0,
```
