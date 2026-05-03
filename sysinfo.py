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
import socket



def collect_sysinfo():
    """Collect system information and return as a dictionary."""
    sysinfo = {}
    sysinfo['hostname'] = socket.gethostname()
    sysinfo['OS'] = platform.system()
    sysinfo['OS_version'] = platform.release()
    sysinfo['CPU_Brand'] = cpuinfo.get_cpu_info().get('brand_raw')
    sysinfo['CPU_Arch'] = cpuinfo.get_cpu_info().get('arch')
    sysinfo['CPU_Cores'] = cpuinfo.get_cpu_info().get('count')
    sysinfo['RAM_Total'] = psutil.virtual_memory().total / (1024**3)
    sysinfo['RAM_Used'] = psutil.virtual_memory().used / (1024**3)
    sysinfo['RAM_Free'] = psutil.virtual_memory().available / (1024**3)
    sysinfo['RAM_Percent_Used'] = psutil.virtual_memory().percent
    sysinfo['Disk_Percent_Used'] = psutil.disk_usage('/').percent
    sysinfo['Disk_Total'] = psutil.disk_usage('/').total / (1024**3)
    sysinfo['Disk_Free'] = psutil.disk_usage('/').free / (1024**3)
    sysinfo['Disk_Mounted'] = psutil.disk_usage('/')
    sysinfo['IP_Address'] = get_local_ip_address()
    sysinfo['MAC_Address'] = get_mac_address()
    sysinfo['Uptime'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    return sysinfo

def get_local_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_mac_address():
    local_ip = get_local_ip_address()
    for interface, addrs in psutil.net_if_addrs().items():
        for row in addrs:
            if row.family == socket.AF_INET and row.address == local_ip:
                break
        else:
            continue  # inner loop finished without break → no IP on this iface

        for row in addrs:
            if row.family == psutil.AF_LINK:
                return row.address
        break

    return None


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