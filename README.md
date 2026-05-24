# Network Reconnaissance Tool (`netrecon.py`)

`netrecon.py` is a command-line tool that gathers information about a target IP address from two sources:

1. **Nmap** — finds open ports, service names, and port states on the target.
2. **ip-api.com** — looks up geographic and network information (country, region, city, ISP).

It prints a human-readable summary to your terminal and saves everything to a CSV file you choose.

This README explains what you need installed, how to run the tool step by step, and how the script works internally.

---

## Table of contents

- [What this tool does](#what-this-tool-does)
- [System requirements](#system-requirements)
- [Installation](#installation)
- [How to run it](#how-to-run-it)
- [Understanding the output](#understanding-the-output)
- [How the script works](#how-the-script-works)
- [Choosing a target IP](#choosing-a-target-ip)
- [Troubleshooting](#troubleshooting)
- [Legal and ethical use](#legal-and-ethical-use)

---

## What this tool does

When you run:

```bash
python netrecon.py <target_ip> <output.csv>
```

the program will:

1. Check that `<target_ip>` is a valid IP address.
2. Query [ip-api.com](http://ip-api.com) for geolocation data.
3. Run an Nmap port scan against the target.
4. Print a summary (geolocation + open ports) to the screen.
5. Write the same data to `<output.csv>`.

**Important:** A full port scan (`-p-`) can take a long time (many minutes) because it checks all 65,535 TCP ports. That is expected behavior with the current scan settings.

---

## System requirements

### Hardware and OS

| Requirement | Details |
|-------------|---------|
| **Operating system** | Linux (recommended), macOS, or WSL on Windows. The script was developed and tested on Linux (e.g. Raspberry Pi OS, Ubuntu). |
| **CPU / RAM** | Any modest machine is fine; Nmap is the slow part, not Python. |
| **Disk space** | Minimal (a few megabytes for Python packages and small CSV output files). |
| **Network** | Active internet connection (required for geolocation via ip-api.com). The machine must be able to reach the target IP for scanning. |

### Software you must install

| Software | Minimum version | Why you need it |
|----------|-----------------|-----------------|
| **Python** | 3.8 or newer | Runs the script. Check with `python3 --version`. |
| **Nmap** | 7.x recommended | Performs the actual port scan. `python-nmap` is only a wrapper; Nmap must be installed separately. |
| **pip** | (bundled with Python) | Installs Python libraries from `requirements.txt`. |

### Python packages (installed via pip)

Listed in `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `python-nmap` | Lets Python call the Nmap program and read scan results. |
| `requests` | Sends HTTP requests to ip-api.com for geolocation. |
| `paramiko` | Listed for optional future SSH features; **not used** by the current version of `netrecon.py`. |

The standard library module `ipaddress` (used for IP validation) ships with Python—you do not install it separately.

### Permissions

- **Geolocation** — No special permissions; only needs outbound HTTP access.
- **Nmap scanning** — Depending on your OS and scan options, you may need to run the scan as root (see [Troubleshooting](#troubleshooting)):
  ```bash
  sudo python3 netrecon.py <target_ip> output.csv
  ```
  Only scan systems you own or have explicit permission to test.

---

## Installation

Follow these steps from the project folder (the directory that contains `netrecon.py`).

### 1. Install Nmap (system package)

**Debian / Ubuntu / Raspberry Pi OS:**

```bash
sudo apt update
sudo apt install -y nmap
```

**Fedora:**

```bash
sudo dnf install -y nmap
```

**macOS (Homebrew):**

```bash
brew install nmap
```

Verify Nmap is installed:

```bash
nmap --version
```

### 2. Clone or download this repository

```bash
cd ~/projects/sprints_scripts
```

(Use your actual path if different.)

### 3. Create a virtual environment (recommended)

A virtual environment keeps project dependencies separate from system Python.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (Command Prompt):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Your prompt should show `(.venv)` when the environment is active.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Confirm everything works

Quick check that Python can import the needed modules:

```bash
python3 -c "import nmap, requests; print('OK')"
```

---

## How to run it

### Basic command

```bash
python netrecon.py <target_ip> <output.csv>
```

| Argument | Description | Example |
|----------|-------------|---------|
| `target_ip` | IPv4 or IPv6 address to scan | `45.33.32.156` |
| `output.csv` | Path to the CSV file to create (overwritten if it exists) | `results.csv` |

### Examples

**Scan a public server and save to `public_ip.csv`:**

```bash
python netrecon.py 45.33.32.156 public_ip.csv
```

**Scan your own machine (localhost) — good for testing Nmap:**

```bash
python netrecon.py 127.0.0.1 localhost.csv
```

Geolocation will **not** work for `127.0.0.1` or private IPs (see below); the port scan still runs.

**If Nmap reports permission errors, use sudo:**

```bash
sudo $(which python3) netrecon.py 127.0.0.1 localhost.csv
```

If you use a virtual environment, activate it first, then:

```bash
sudo .venv/bin/python netrecon.py 127.0.0.1 localhost.csv
```

### What you will see

While the script runs:

1. Geolocation usually finishes in a few seconds.
2. Nmap runs next and may take a long time for a full port scan.

Example terminal output (values will vary):

```
Target: 45.33.32.156
Output file: public_ip.csv
Country: United States
Region:  California
City:    Fremont
ISP:     Akamai Technologies, Inc.
Open ports: 3
  22/ssh (open)
  80/http (open)
  443/https (open)

Wrote results to public_ip.csv
```

---

## Understanding the output

### CSV file format

The first row is always a **header**. Each following row is one **open port**.

**When geolocation succeeds**, columns are:

| Column | Meaning |
|--------|---------|
| `port` | Port number (e.g. `22`) |
| `service` | Service name Nmap detected (e.g. `ssh`) |
| `state` | Port state (only `open` ports are written) |
| `country` | Country name from ip-api.com |
| `region` | Region or state name |
| `city` | City name |
| `isp` | Internet service provider |

Example:

```csv
port,service,state,country,region,city,isp
22,ssh,open,United States,California,Fremont,Akamai Technologies, Inc.
80,http,open,United States,California,Fremont,Akamai Technologies, Inc.
```

Geolocation columns are repeated on every port row so all information stays in one file.

**When geolocation fails** (private IP, no internet, API error), the CSV only has:

```csv
port,service,state
22,ssh,open
```

### Terminal summary

The screen output mirrors the CSV: target IP, output path, geolocation (if available), then a list of open ports.

---

## How the script works

High-level flow:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Parse args  │────▶│ Validate IP      │────▶│ Geolocation │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                    │
┌─────────────┐     ┌──────────────────┐            │
│ Print summary│◀───│ Write CSV        │◀───┬───────┘
└─────────────┘     └──────────────────┘    │
                                            ▼
                                    ┌─────────────┐
                                    │ Nmap scan   │
                                    └─────────────┘
```

### Functions in `netrecon.py`

| Function | Role |
|----------|------|
| `parse_args()` | Reads `target_ip` and `output_csv` from the command line using `argparse`. |
| `validate_ip(ip)` | Uses Python’s `ipaddress` module to reject invalid IPs before any network activity. |
| `get_geolocation(ip)` | Sends an HTTP GET request to `http://ip-api.com/json/{ip}`. Returns a dictionary with `country`, `region`, `city`, and `isp`, or `None` on failure. Uses a 10-second timeout so the script does not hang forever. |
| `scan(scanner, target_ip)` | Runs Nmap with arguments `-p- -sV -sC`: all ports, service/version detection, and default scripts. Returns a nested dictionary from `python-nmap`. |
| `csv_output(...)` | Opens the output CSV, writes the header, loops through Nmap’s scan structure, and writes one row per open port (plus geolocation columns when available). |
| `print_summary(...)` | Prints the same information in a readable format for the user. |
| `main()` | Orchestrates the steps above in order: validate → geolocate → scan → save CSV → print summary. |

### How Nmap results are parsed

Nmap returns a large nested dictionary. The script looks under `result["scan"][target_ip]` and walks each protocol section (e.g. `tcp`). It skips metadata keys like `hostnames`, `addresses`, `status`, and `vendor`. For each port, it only records entries where `state` is `"open"`.

### How geolocation works

The script calls the free [ip-api.com](http://ip-api.com) JSON API. No API key is required. The service limits free use to about **45 requests per minute** per client IP. Only scan targets you are allowed to look up.

Private and reserved addresses (`127.0.0.1`, `10.x.x.x`, `192.168.x.x`, etc.) return a failed status from the API; the script continues with the port scan and writes CSV without geo columns.

### Scan options explained

Current Nmap arguments in `scan()`:

| Flag | Meaning |
|------|---------|
| `-p-` | Scan all 65535 TCP ports |
| `-sV` | Detect service/version on open ports |
| `-sC` | Run default Nmap scripts (safe reconnaissance scripts) |

These settings are thorough but slow. They are appropriate for a lab assignment; for faster tests you would use a smaller port range (that would require editing `netrecon.py`).

---

## Choosing a target IP

| Target | Port scan | Geolocation |
|--------|-----------|-------------|
| Your own cloud VM (e.g. AWS) public IP | Yes | Yes |
| `127.0.0.1` (localhost) | Yes (good for first test) | No (private range) |
| Classmate’s machine | Only with **their permission** | Yes if public IP |
| Random internet hosts | **Do not scan without permission** | — |

**Best practice:** Test Nmap on `127.0.0.1` first, then use a **public** IP you control for the full assignment (scan + geolocation).

---

## Troubleshooting

| Problem | Likely cause | What to try |
|---------|--------------|-------------|
| `nmap: command not found` or `Nmap error` | Nmap not installed | Install Nmap (see [Installation](#installation)). |
| `ModuleNotFoundError: No module named 'nmap'` | Python packages not installed | Activate `.venv` and run `pip install -r requirements.txt`. |
| `Invalid IP address` | Typo in IP argument | Use a valid IPv4/IPv6 address, e.g. `8.8.8.8`. |
| `Geolocation lookup failed: private range` | Target is localhost or LAN IP | Use a public IP for geo, or ignore geo for local tests. |
| `Geolocation lookup failed: ...` (network) | No internet or firewall | Check connectivity; try `curl http://ip-api.com/json/8.8.8.8`. |
| Scan runs but finds no ports | Target has a firewall or no services | Expected on hardened hosts; try `127.0.0.1`. |
| Scan very slow | Full port scan (`-p-`) | Wait, or scan a machine with fewer open ports for testing. |
| Nmap permission / capability errors | Needs raw sockets | Run with `sudo` as shown above. |
| `Error: no scan data for <ip>` | Host down, blocked, or wrong IP | Ping the host; confirm IP and network path. |

---

## Legal and ethical use

Only use this tool on networks and systems where you have **explicit authorization** (your own lab machines, assigned class targets with permission, etc.). Unauthorized port scanning may violate policies or laws. This tool is for educational use in a cybersecurity course.

---

## Project information

- **Course:** BAS Cybersecurity Automation — Sprint 3
- **Repository branch (submission):** `sprint3-netrecon`
- **Author:** Quang Do

## License

MIT License — see the header in `netrecon.py`.
