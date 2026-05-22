#!/usr/bin/python3
# netrecon.py:
# Licensed under the MIT License (https://opensource.org/license/mit)
# QuangDo-date-here: V1.0.0
import argparse
import nmap
import csv
import ipaddress
import sys
import requests


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Network Reconnaissance Tool")
    parser.add_argument("target_ip", help="Target IP address to scan")
    parser.add_argument("output_csv", help="Path to output CSV file")
    return parser.parse_args()


def validate_ip(ip):
    """Validate IP address"""
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print(f"Invalid IP address: {ip}", file=sys.stderr)
        sys.exit(1)


def csv_output(result, output_path, host=None, geolocation=None):
    """Write scan and geolocation results to CSV file."""
    headers = ["port", "service", "state"]
    geo_fields = []
    if geolocation:
        headers.extend(["country", "region", "city", "isp"])
        geo_fields = [
            geolocation["country"],
            geolocation["region"],
            geolocation["city"],
            geolocation["isp"],
        ]
    with open(output_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        scan_data = result.get("scan", {})
        hosts = [host] if host else scan_data.keys()
        for h in hosts:
            if h not in scan_data:
                continue
            host_data = scan_data[h]
            for proto, ports in host_data.items():
                if proto in ("hostnames", "addresses", "status", "vendor"):
                    continue
                if not isinstance(ports, dict):
                    continue
                for port, info in sorted(ports.items()):
                    if info.get("state") == "open":
                        row = [port, info.get("name", ""), info["state"]]
                        if geo_fields:
                            row.extend(geo_fields)
                        w.writerow(row)


def scan(scanner, target_ip):
    """Scan target IP for open ports"""
    return scanner.scan(target_ip, arguments="-p- -sV -sC")


def print_summary(target_ip, output_csv, result, geolocation=None):
    """Print scan summary to the terminal."""
    print(f"Target: {target_ip}")
    print(f"Output file: {output_csv}")
    if geolocation:
        print(f"Country: {geolocation['country']}")
        print(f"Region:  {geolocation['region']}")
        print(f"City:    {geolocation['city']}")
        print(f"ISP:     {geolocation['isp']}")
    else:
        print("Geolocation: unavailable")

    scan_data = result.get("scan", {})
    if target_ip not in scan_data:
        print("Open ports: 0")
        return

    host_data = scan_data[target_ip]
    open_ports = []

    for proto, ports in host_data.items():
        if proto in ("hostnames", "addresses", "status", "vendor"):
            continue
        if not isinstance(ports, dict):
            continue
        for port, info in sorted(ports.items()):
            if info.get("state") == "open":
                service = info.get("name", "") or "unknown"
                open_ports.append((port, service, info["state"]))

    print(f"Open ports: {len(open_ports)}")
    if not open_ports:
        print("  (none)")
    else:
        for port, service, state in open_ports:
            print(f"  {port}/{service} ({state})")


def get_geolocation(ip):
    """Query ip-api.com for country, region, city, and ISP."""
    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,message,country,regionName,city,isp"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"Geolocation lookup failed: {e}", file=sys.stderr)
        return None
    if data.get("status") != "success":
        print(
            f"Geolocation lookup failed: {data.get('message', 'unknown error')}",
            file=sys.stderr,
        )
        return None
    return {
        "country": data.get("country", ""),
        "region": data.get("regionName", ""),
        "city": data.get("city", ""),
        "isp": data.get("isp", ""),
    }


def main():
    """Main function"""
    args = parse_args()
    validate_ip(args.target_ip)
    geolocation = get_geolocation(args.target_ip)
    scanner = nmap.PortScanner()
    try:
        result = scan(scanner, args.target_ip)
    except nmap.PortScannerError as e:
        print(f"Nmap error: {e}", file=sys.stderr)
        sys.exit(1)
    if args.target_ip not in result.get("scan", {}):
        print(f"Error: no scan data for {args.target_ip}.", file=sys.stderr)
        sys.exit(1)
    csv_output(result, args.output_csv, host=args.target_ip, geolocation=geolocation)
    print_summary(args.target_ip, args.output_csv, result, geolocation)
    print(f"\nWrote results to {args.output_csv}")


if __name__ == "__main__":
    main()
