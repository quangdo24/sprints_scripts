#!/usr/bin/python3
# netrecon.py:
# Licensed under the MIT License (https://opensource.org/license/mit)
# QuangDo-date-here: V1.0.0 
import argparse
import nmap
import json


sc = nmap.PortScanner()






def main():
    #test here for nmap: **port number**, **service name**, and **state**.
    result = sc.scan('127.0.0.1', arguments='-p- -sV -sC')
    print(json.dumps(result, indent=4, default=str))

if __name__ == "__main__":
    main()