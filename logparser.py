#!/usr/bin/python3
# <REPLACE THIS LINE WITH A DESCRIPTION OF SCRIPT>
# Licensed under the MIT License (https://opensource.org/license/mit)
# Author: Quang Do | Version: 1.0.0 | Date: 2026-04-13
# Set up initial variables and imports
import sys
import re
import csv

# Script/Library Functions
def main():
    # Check if 2 arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python logparser.py <filename> <output.csv>")
        sys.exit(1)

    log_file = sys.argv[1]
    output_file = sys.argv[2]

    parse_log(log_file, output_file)


def parse_log(log_file, output_file):
    """Opens log file, finds failed SSH attempts, writes results to screen and CSV."""

    # Define regex pattern to find failed SSH attempts
    pattern = re.compile(
        r'^(\w+ \d+ \d+:\d+:\d+).*Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)'
    )

    # Try to open the log file
    try:
        logfile = open(log_file, 'r')
    except FileNotFoundError:
        print(f"Error: {log_file} not found")
        sys.exit(1)

    # Try to open output file
    try:
        csvfile = open(output_file, 'w', newline='')
    except FileNotFoundError:
        print(f"Error: {output_file} not found")
        csvfile.close()
        sys.exit(1)

    writer = csv.writer(csvfile)
    writer.writerow(['Timestamp', 'Username', 'IP Address'])

    match_count = 0

    for line in logfile:
        match = pattern.search(line)
        if match:
            timestamp = match.group(1)
            username = match.group(2)
            source_ip = match.group(3)
            
            print(f"Timestamp: {timestamp}, Username: {username}, Source IP: {source_ip}")
            writer.writerow([timestamp,username,source_ip])
            match_count += 1
    
    logfile.close()
    csvfile.close()

    print(f'\nDone. {match_count} failed SSH attempts found and written to {output_file}')

            
# Run main() if script called directly, else use as a library to be imported
if __name__ == '__main__':
    main()
