#!/usr/bin/python3
# Description of this script goes here
# Licensed under the MIT License (https://opensource.org/license/mit)
# QuangDo-20260426: V1.0.0

# Set up initial variables and imports
import os
import platform
import csv
import datetime
import psutil
import cpuinfo
import socket
import time
import argparse
import json


def collect_sysinfo():
    """Collect system information and return as a dictionary."""
    sysinfo = {}
    sysinfo["HOSTNAME"] = socket.gethostname()
    sysinfo["OS"] = platform.system()
    sysinfo["OS_version"] = platform.release()
    sysinfo["KERNEL_VERSION"] = platform.release()
    sysinfo["CPU_BRAND"] = cpuinfo.get_cpu_info().get("brand_raw")
    sysinfo["CPU_ARCH"] = cpuinfo.get_cpu_info().get("arch")
    sysinfo["CPU_CORES"] = cpuinfo.get_cpu_info().get("count")
    sysinfo["RAM_TOTAL"] = psutil.virtual_memory().total / (1024**3)
    sysinfo["RAM_USED"] = psutil.virtual_memory().used / (1024**3)
    sysinfo["RAM_FREE"] = psutil.virtual_memory().available / (1024**3)
    sysinfo["RAM_Percent_Used"] = psutil.virtual_memory().percent
    sysinfo["DISK_PERCENT_USED"] = psutil.disk_usage("/").percent
    sysinfo["DISK_TOTAL"] = psutil.disk_usage("/").total / (1024**3)
    sysinfo["DISK_FREE"] = psutil.disk_usage("/").free / (1024**3)
    sysinfo["DISK_MOUNTED"] = psutil.disk_usage("/")
    sysinfo["IP_ADDRESS"] = get_local_ip_address()
    sysinfo["MAC_ADDRESS"] = get_mac_address()
    sysinfo["UPTIME"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    sysinfo["TOP_5_CPU_PROCESSES"] = get_top_5_processes()
    return sysinfo


def print_sysinfo(info):
    """Print the system information to the console in human readable format."""
    print("=" * 50)
    print(" " * 15 + "SYSTEM INFORMATION")
    print("=" * 50)
    print()
    print(f"HOSTNAME:                   {info['HOSTNAME']}")
    print(f"OS type and version:        {info['OS']} {info['OS_version']}")
    print(f"Kernel Version:             {info['KERNEL_VERSION']}")
    print(f"CPU Cores:                  {info['CPU_CORES']}")
    print(f"Total RAM (GB):             {info['RAM_TOTAL']:.2f}")
    print(f"RAM Used (GB):              {info['RAM_USED']:.2f}")
    print(f"RAM Free (GB):              {info['RAM_FREE']:.2f}")
    print(f"Disk total (GB):            {info['DISK_TOTAL']:.2f}")
    print(f"Disk free (GB):             {info['DISK_FREE']:.2f}")
    print(f"Primary IP address:         {info['IP_ADDRESS']}")
    print(f"Primary MAC address:        {info['MAC_ADDRESS']}")
    print(f"Uptime:                     {info['UPTIME']}")
    print()
    print("Top 5 Processes by CPU Usage:")
    print(f"{'PID':<30}{'Name':<30}CPU%")
    print("-" * 70)
    for p in info["TOP_5_CPU_PROCESSES"]:
        print(f"{p['pid']:<30}{p['name']:<30}{p['cpu_percent']}%")


def write_sysinfo_json(info, filepath):
    """Writes sysinfo to JSON"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f"Wrote JSON to: {filepath}")


def write_sysinfo_csv(info, filepath):
    """Writes sysinfo to CSV"""
    row = {key: str(value) for key, value in info.items()}

    fieldnames = list(row.keys())

    with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

    print(f"Wrote CSV to: {filepath}")


def get_top_5_processes():
    """Return the five processes with highest CPU usage (sampled over ~0.1s)."""
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    time.sleep(0.1)
    rows = []
    for p in psutil.process_iter(attrs=["pid", "name", "memory_percent"]):
        try:
            cpu = p.cpu_percent(interval=None)
            rows.append(
                {
                    "pid": p.info["pid"],
                    "name": p.info["name"],
                    "cpu_percent": cpu,
                    "memory_percent": p.info["memory_percent"],
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    rows.sort(key=lambda r: r["cpu_percent"], reverse=True)
    return rows[:5]


def get_local_ip_address():
    """Get the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_mac_address():
    """Get the MAC address of the machine."""
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
    """Get the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))


# Script/Library Functions
def main():
    """Main function to parse the log file and write the results to a CSV file."""
    parser = argparse.ArgumentParser(
        description="Collect system information (hardware, OS, disk, network, top CPU processes)."
    )

    parser.add_argument(
        "-s",
        "--screen",
        action="store_true",
        help="Print system information to console in a human readable format.",
    )
    parser.add_argument(
        "-c", "--csv", action="store_true", help="writes to sysinfo.csv"
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="writes to sysinfo.json"
    )

    args = parser.parse_args()

    if not any([args.screen, args.csv, args.json]):
        parser.print_help()
        return

    sysinfo = collect_sysinfo()

    if args.screen:
        print_sysinfo(sysinfo)

    if args.csv:
        csv_path = os.path.join(_script_dir(), "sysinfo.csv")
        write_sysinfo_csv(sysinfo, csv_path)

    if args.json:
        json_path = os.path.join(_script_dir(), "sysinfo.json")
        write_sysinfo_json(sysinfo, json_path)


# Run main() if script called directly, else use as a library to be imported
if __name__ == "__main__":
    """Main function to parse the log file and write the results to a CSV file."""
    main()
