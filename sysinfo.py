#!/usr/bin/python3
# Description of this script goes here
# Licensed under the MIT License (https://opensource.org/license/mit)
# QuangDo-20260426: V1.0.0

# Set up initial variables and imports
import os
import platform
import sys
import platform
import socket
import csv
import json
import datetime
import psutil
import cpuinfo


def collect_sysinfo():
    """Collect system information and return as a dictionary."""
    sysinfo = {}
    sysinfo['hostname'] = socket.gethostname()
    sysinfo['OS'] = platform.system()
    sysinfo['OS_version'] = platform.release()
    sysinfo['CPU_Brand'] = cpuinfo.get_cpu_info().get('brand_raw')
    sysinfo['CPU_Arch'] = cpuinfo.get_cpu_info().get('arch')
    sysinfo['CPU_Cores'] = cpuinfo.get_cpu_info().get('count')

    
    return sysinfo


# Helper: directory containing this script (for output file paths).
def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))

# Script/Library Functions
def main():
    """Main function to parse the log file and write the results to a CSV file."""
    sysinfo = collect_sysinfo()
    print(sysinfo)



            
# Run main() if script called directly, else use as a library to be imported
if __name__ == '__main__':
    main()