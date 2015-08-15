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

#*** Import sys and getopt for command line argument parsing:
import sys, getopt

def main(argv):
    """
    Main function of mosp
    """
    version = "0.1.0"
    interval = 1
    max_run_time = 0
    finished = 0
    first_time = 1
    output_file = 0
    output_file_enabled = 0
    header_row = 1
    prev_sin = 0
    prev_sout = 0
    prev_pin = 0
    prev_pout = 0
    interface = 'eth1'

    #*** Get the hostname for use in filenames etc:
    hostname = socket.gethostname()

    #*** Start by parsing command line parameters:
    try:
        opts, args = getopt.getopt(argv, "hu:m:ni:w:Wjv",
                                ["help",
                                "url=",
                                "max-run-time=",
                                "no-keepalive",
                                "interval=",
                                "output-file=",
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
        elif opt == '-V':
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
        elif opt in ("-j", "--no-header-row"):
            header_row = 0

    print "\nMeasure Operating System Performance (mosp) version", \
                                         version

    #*** Display output filename:
    if output_file_enabled:
        print "Results filename is", output_file
    else:
        print "Not outputing results to file, as option not selected"

    if not header_row:
        print "Not writing a header row to CSV"

    #*** Use this if max_run_time is set:
    initial_time = time.time()

    #*** Start the loop:
    while not finished:
        timenow = datetime.datetime.now()
        timestamp = timenow.strftime("%H:%M:%S")
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
        #*** Network Packets Per Second:
        os_net = psutil.net_io_counters(pernic=True)
        if prev_pin:
           delta_pin = os_net[interface].packets_recv - prev_pin
        else:
            delta_pin = 0
        prev_pin = os_net[interface].packets_recv
        if prev_pout:
           delta_pout = os_net[interface].packets_sent - prev_pout
        else:
            delta_pout = 0
        prev_pout = os_net[interface].packets_sent

        end_time = time.time()
        total_time = end_time - start_time
        #*** Put the stats into a nice string for printing and
        #***  writing to file:
        result_csv = str(timestamp) \
                    + "," + str(os_cpu) \
                    + "," + str(delta_sin) \
                    + "," + str(delta_sout) \
                    + "," + str(delta_pin) \
                    + "," + str(delta_pout) \
                    + "\n"
        result_kvp = str(timestamp) \
                    + " cpu=" + str(os_cpu) \
                    + " swap-in=" + str(delta_sin) \
                    + " swap-out=" + str(delta_sout) \
                    + " pkt-in=" + str(delta_pin) \
                    + " pkt-out=" + str(delta_pout)
        print result_kvp
        if output_file_enabled:
            #*** Header row in CSV:
            if first_time and header_row:
                #*** Write a header row to CSV:
                header_csv = "time," + hostname + "-cpu," + \
                                hostname + "-swap-in," + \
                                hostname + "-swap-out," + \
                                hostname + "-pkt-in," + \
                                hostname + "-pkt-out\n"
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
 -h, --help          Display this help and exit
 -m, --max-run-time  Maximum time to run for before exiting
                       (default is infinite)
 -i, --interval      Interval between requests in seconds
                       (default is 1)
 -w, --output-file   Specify an output filename
 -W                  Output results to default filename
                       default format is:
                       mosp-HOSTNAME-YYYYMMDD-HHMMSS.csv
 -j  --no-header-row       Suppress writing header row into CSV
 -v, --version       Output version information and exit

 Results are written in following CSV format:
 <timestamp>,<FOO>,
    <elapsed_time>
 """
    return()

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])
