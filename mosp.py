#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Measure Operating System Performance (mosp)
.
This code measures operating system performance,
including CPU, memory, disk and network, and
outputs stats to screen and optionally to file
too for use in performance analysis
.
Uses the psutil library
.
Install psutil (Ubuntu) if you don't already have it:
    sudo apt-get install python-dev
    sudo pip install psutil
.
Do not use this code for production deployments - it
is proof of concept code and carries no warrantee
whatsoever. You have been warned.
"""

#*** Import psutil library:
import psutil

import socket
import datetime
import time

#*** For file path:
import os

#*** Import sys and getopt for command line argument parsing:
import sys, getopt

#*** For ordered dictionaries:
import collections

def main(argv):
    """
    Main function of mosp
    """
    version = "0.1.2"
    interval = 1
    max_run_time = 0
    finished = 0
    first_time = 1
    output_file = 0
    output_file_enabled = 0
    output_path = 0
    header_row = 1
    prev_sin = 0
    prev_sout = 0

    #*** Get the hostname for use in filenames etc:
    hostname = socket.gethostname()

    #*** Start by parsing command line parameters:
    try:
        opts, args = getopt.getopt(argv, "hu:m:ni:w:Wb:jv",
                                ["help",
                                "url=",
                                "max-run-time=",
                                "no-keepalive",
                                "interval=",
                                "output-file=",
                                "output-path=",
                                "no-header-row",
                                "version"])
    except getopt.GetoptError as err:
        print "mosp: Error with options:", err
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-v", "--version"):
            print 'mosp.py version', version
            sys.exit()
        elif opt in ("-m", "--max-run-time"):
            max_run_time = float(arg)
        elif opt in ("-i", "--interval"):
            interval = float(arg)
        elif opt in ("-w", "--output-file"):
            output_file = arg
            output_file_enabled = 1
        elif opt == "-W":
            output_file = "mosp-" + hostname + "-" + \
                             time.strftime("%Y%m%d-%H%M%S.csv")
            output_file_enabled = 1
        elif opt in ("-b", "--output-path"):
            output_path = arg
        elif opt in ("-j", "--no-header-row"):
            header_row = 0

    print "\nMeasure Operating System Performance (mosp) version", \
                                         version

    #*** Display output filename:
    if output_file_enabled:
        if output_path:
            output_file = os.path.join(output_path, output_file)
        print "Results filename is", output_file
    else:
        print "Not outputing results to file, as option not selected"

    if not header_row:
        print "Not writing a header row to CSV"

    #*** Use this if max_run_time is set:
    initial_time = time.time()

    #*** Instantiate classes:
    nics = Nics()

    #*** Start the loop:
    while not finished:
        timenow = datetime.datetime.now()
        timestamp = timenow.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        start_time = time.time()
        #*** CPU percentage with psutil:
        os_cpu = psutil.cpu_percent()
        #*** Swap rates with psutil, calculate differences:
        os_mem_swap = psutil.swap_memory()
        if prev_sin:
            delta_sin = os_mem_swap.sin - prev_sin
        else:
            delta_sin = 0
        prev_sin = os_mem_swap.sin
        if prev_sout:
            delta_sout = os_mem_swap.sout - prev_sout
        else:
            delta_sout = 0
        prev_sout = os_mem_swap.sout
        #*** Update network measurements:
        nics.update()

        #*** Put the stats into a nice string for printing and
        #***  writing to file:
        result_csv = str(timestamp) \
                    + "," + str(os_cpu) \
                    + "," + str(delta_sin) \
                    + "," + str(delta_sout) \
                    + "," + nics.csv() \
                    + "\n"
        result_kvp = str(timestamp) \
                    + " cpu=" + str(os_cpu) \
                    + " swap-in=" + str(delta_sin) \
                    + " swap-out=" + str(delta_sout) \
                    + " " + nics.kvp()
        print result_kvp
        if output_file_enabled:
            #*** Header row in CSV:
            if first_time and header_row:
                #*** Write a header row to CSV:
                header_csv = "time," + hostname + "-cpu," + \
                                hostname + "-swap-in," + \
                                hostname + "-swap-out," + \
                                nics.csv_header(hostname) \
                                + "\n"
                first_time = 0
                with open(output_file, 'a') as the_file:
                    the_file.write(header_csv)

            #*** Write a data row to CSV:
            with open(output_file, 'a') as the_file:
                the_file.write(result_csv)

        if max_run_time:
            if (start_time - initial_time) > max_run_time:
                break

        #*** Sleep for interval seconds:
        time.sleep(interval)

def print_help():
    """
    Print out the help instructions
    """
    print """
Measure Operating System Performance (mosp)
-------------------------------------------

Use this program to measure and report on operating system
performance.

This code measures operating system performance,
including CPU, memory, disk and network, and
outputs stats to screen and optionally to file
too for use in performance analysis

Uses the psutil library

Install psutil (Ubuntu) if you don't already have it:
    sudo apt-get install python-dev
    sudo pip install psutil

Usage:
  python mosp.py [options]

Example usage:
  python mosp.py -W -i 2

Options:
 -h  --help          Display this help and exit
 -m  --max-run-time  Maximum time to run for before exiting
                       (default is infinite)
 -i  --interval      Interval between requests in seconds
                       (default is 1)
 -w  --output-file   Specify an output filename
 -W                  Output results to default filename
                       default format is:
                       mosp-HOSTNAME-YYYYMMDD-HHMMSS.csv
 -b  --output-path         Specify path to output file directory
 -j  --no-header-row       Suppress writing header row into CSV
 -v  --version       Output version information and exit

 Results are written in following CSV format:
 <timestamp>,<FOO>,
    <elapsed_time>
 """
    return()

class Nics(object):
    """
    Represents the Network Interface Cards (NICS)
    on the system
    """
    def __init__(self):
        """
        Initialise the class
        """
        self.prev_pkts_in = collections.OrderedDict()
        self.delta_pkts_in = collections.OrderedDict()
        self.prev_pkts_out = collections.OrderedDict()
        self.delta_pkts_out = collections.OrderedDict()
        self.prev_bytes_in = collections.OrderedDict()
        self.delta_bytes_in = collections.OrderedDict()
        self.prev_bytes_out = collections.OrderedDict()
        self.delta_bytes_out = collections.OrderedDict()
        self.interfaces = []

        #*** Build a list of the NICs that will be used for ordering:
        os_net = psutil.net_io_counters(pernic=True)
        for interface in os_net:
            self.interfaces.append(interface)

    def update(self):
        """
        Update the stats for NICs from psutil
        """
        #*** Get dictionary of NICs with results from psutil:
        os_net = psutil.net_io_counters(pernic=True)
        #*** Update our variables including delta values:
        for interface in os_net:
            #*** Packets in:
            pkts_in = os_net[interface].packets_recv

            #*** Ensure keys in dicts:
            if not interface in self.prev_pkts_in:
                self.prev_pkts_in[interface] = 0
            if not interface in self.delta_pkts_in:
                self.delta_pkts_in[interface] = 0

            #*** Calculate difference in packets in:
            if self.prev_pkts_in[interface]:
                self.delta_pkts_in[interface] = \
                                         pkts_in - self.prev_pkts_in[interface]
            else:
                self.delta_pkts_in[interface] = 0
            self.prev_pkts_in[interface] = pkts_in

            #*** Packets out:
            pkts_out = os_net[interface].packets_sent

            #*** Ensure keys in dicts:
            if not interface in self.prev_pkts_out:
                self.prev_pkts_out[interface] = 0
            if not interface in self.delta_pkts_out:
                self.delta_pkts_out[interface] = 0

            #*** Calculate difference in packets out:
            if self.prev_pkts_out[interface]:
                self.delta_pkts_out[interface] = \
                                       pkts_out - self.prev_pkts_out[interface]
            else:
                self.delta_pkts_out[interface] = 0
            self.prev_pkts_out[interface] = pkts_out

            #*** Bytes in:
            bytes_in = os_net[interface].bytes_recv

            #*** Ensure keys in dicts:
            if not interface in self.prev_bytes_in:
                self.prev_bytes_in[interface] = 0
            if not interface in self.delta_bytes_in:
                self.delta_bytes_in[interface] = 0

            #*** Calculate difference in bytes in:
            if self.prev_bytes_in[interface]:
                self.delta_bytes_in[interface] = \
                        bytes_in - self.prev_bytes_in[interface]
            else:
                self.delta_bytes_in[interface] = 0
            self.prev_bytes_in[interface] = bytes_in

            #*** Bytes out:
            bytes_out = os_net[interface].bytes_sent

            #*** Ensure keys in dicts:
            if not interface in self.prev_bytes_out:
                self.prev_bytes_out[interface] = 0
            if not interface in self.delta_bytes_out:
                self.delta_bytes_out[interface] = 0

            #*** Calculate difference in bytes out:
            if self.prev_bytes_out[interface]:
                self.delta_bytes_out[interface] = \
                       bytes_out - self.prev_bytes_out[interface]
            else:
                self.delta_bytes_out[interface] = 0
            self.prev_bytes_out[interface] = bytes_out

    def csv_header(self, hostname):
        """
        Get a CSV header row string for all NICs
        """
        result = ""
        for interface in self.interfaces:
            result += hostname + "-pkts-in[" + interface + "],"
            result += hostname + "-pkts-out[" + interface + "],"
            result += hostname + "-bytes-in[" + interface + "],"
            result += hostname + "-bytes-out[" + interface + "],"
        return result

    def csv(self):
        """
        Get a CSV string of statistics for all NICs
        """
        result = ""
        for interface in self.interfaces:
            result += str(self.delta_pkts_in[interface]) + ","
            result += str(self.delta_pkts_out[interface]) + ","
            result += str(self.delta_bytes_in[interface]) + ","
            result += str(self.delta_bytes_out[interface]) + ","
        return result

    def kvp(self):
        """
        Get a Key-Value Pair (KVP) string of statistics for all NICs
        """
        result = ""
        for interface in self.interfaces:
            result += "pkts-in[" + interface + "]=" + \
                                       str(self.delta_pkts_in[interface]) + " "
            result += "pkts-out[" + interface + "]=" + \
                                      str(self.delta_pkts_out[interface]) + " "
            result += "bytes-in[" + interface + "]=" + \
                                      str(self.delta_bytes_in[interface]) + " "
            result += "bytes-out[" + interface + "]=" + \
                                     str(self.delta_bytes_out[interface]) + " "
        return result

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])

