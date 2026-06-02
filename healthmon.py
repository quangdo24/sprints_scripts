#!/usr/bin/python3
import argparse
import json
import logging
from logging.handlers import SysLogHandler

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Health monitor: disk, memory, CPU load, and services.",
    )

    parser.add_argument(
        "config",
        help="Path to JSON config file (thresholds and log paths)",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Log a human-readable summary report after checks",
    )

    return parser.parse_args()










def main():
    args = parse_args()
    # For now, prove parsing works (remove these once you have logging):
    print(args.config, args.check)  # assignment says no print() long-term
    return 0



if __name__ == "__main__":
    main()