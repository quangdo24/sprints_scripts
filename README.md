# Sprints Scripts

**Quang Do** — BAS Cybersecurity Automation course scripts.

This README focuses on **`sysinfo.py`**: what it does, supported platforms, how to run it, and typical uses.

---

## What `sysinfo.py` does

`sysinfo.py` is a **Python 3** utility that **samples the machine it runs on** and reports:

- **Identity:** hostname  
- **OS:** system name, OS/kernel-style version strings  
- **CPU:** brand string, architecture, core count (via `py-cpuinfo` and `platform`)  
- **Memory:** total, used, free (GB) and percent used (`psutil`)  
- **Disk:** usage of the **root filesystem** `/` — total, free, percent used (`psutil`)  
- **Network:** primary IPv4 used for outbound routing (see Behavioral notes) and matching interface MAC where available  
- **Uptime:** boot time formatted as a timestamp  
- **Processes:** top five processes by CPU% after a short sampling window  

You choose **how** results are delivered:

| Mode | Flag | Result |
|------|------|--------|
| **Screen** | `-s` / `--screen` | Human-readable text printed to the terminal |
| **CSV** | `-c` / `--csv` | One row written to **`sysinfo.csv`** next to the script |
| **JSON** | `-j` / `--json` | Pretty-printed JSON written to **`sysinfo.json`** next to the script |

If you pass **no flags**, the script prints **help** and exits.

Output files are written to the **same directory as `sysinfo.py`**, not necessarily your current working directory.

---

## Operating system compatibility

### Intended and best supported

- **Linux** (including Raspberry Pi OS, Ubuntu, Amazon Linux, etc.) — **primary target.**  
  The script assumes a **Unix-style root mount `/`** for disk stats and uses patterns that match typical Linux networking interfaces.

### Generally usable with caveats

- **macOS** — Usually runs fine; disk usage is still queried on **`/`**. MAC address discovery depends on `psutil` interface layout (often OK).

### Limited / not recommended without edits

- **Windows** — Not the design center of this script. Problems include:
  - Disk usage is hardcoded to **`/`** (Unix root). On Windows you normally query a drive such as **`C:\`**.
  - Process and network behavior differ; some fields may look wrong or require elevation.

**Summary:** Treat this script as **Linux-first** (and Unix-like friendly). For **Windows**, expect to change at least the disk path and retest network/MAC logic.

**Python:** Use **Python 3.8+** (3.10+ recommended). The shebang is `#!/usr/bin/python3`.

---

## Dependencies

Third-party packages are listed in **`requirements.txt`** in this directory (`psutil`, `py-cpuinfo`). Install them into a **virtual environment** (recommended) or your user/site Python — see [How to run](#how-to-run).

Standard library modules used include: `argparse`, `csv`, `datetime`, `json`, `os`, `platform`, `socket`, `time`.

---

## How to run

### 1. Use a virtual environment (recommended)

Keeps packages isolated from system Python. From the **`sprints_scripts`** directory (where `requirements.txt` and `sysinfo.py` live):

**Linux / macOS**

```bash
cd /path/to/sprints_scripts
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (Command Prompt)**

```bat
cd C:\path\to\sprints_scripts
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
cd C:\path\to\sprints_scripts
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

After activation, your shell prompt usually shows `(.venv)`. Use **`deactivate`** to leave the environment.

### 2. Install without a venv (alternative)

If you prefer not to use a virtual environment:

```bash
pip install -r requirements.txt
```

(Run from the directory that contains `requirements.txt`, or pass the full path to the file.)

### 3. Make the script executable (optional, Linux/macOS)

```bash
chmod +x sysinfo.py
```

### 4. Run `sysinfo.py`

With the venv **activated**, use `python` or `python3` as you normally would. You **must** pass at least one of `-s`, `-c`, or `-j`.

**Print to the screen:**

```bash
python3 sysinfo.py --screen
# or
python3 sysinfo.py -s
```

**Write CSV** (`sysinfo.csv` beside the script):

```bash
python3 sysinfo.py --csv
python3 sysinfo.py -c
```

**Write JSON** (`sysinfo.json` beside the script):

```bash
python3 sysinfo.py --json
python3 sysinfo.py -j
```

**Combine modes** (e.g. screen + export JSON):

```bash
python3 sysinfo.py -s -j
```

**Help:**

```bash
python3 sysinfo.py
python3 sysinfo.py --help
```

---

## Output file locations

| File | Created when |
|------|----------------|
| `sysinfo.csv` | `-c` / `--csv` |
| `sysinfo.json` | `-j` / `--json` |

Paths are resolved with the directory containing **`sysinfo.py`** (via `__file__`), so outputs stay with the script even if you run it from another working directory:

```bash
cd /tmp
python3 /path/to/sprints_scripts/sysinfo.py -c
# writes /path/to/sprints_scripts/sysinfo.csv
```

---

## Use cases

- **Inventory / audits:** Quick snapshot of OS, CPU, RAM, disk, and primary IP for documentation or compliance checklists.  
- **Troubleshooting:** See memory pressure, disk usage on `/`, and which processes are using CPU at sample time.  
- **Automation / monitoring glue:** Emit **CSV** or **JSON** for spreadsheets, databases, or other tools that ingest structured data.  
- **Education:** Demonstrates `argparse`, `psutil`, JSON/CSV output, and a pattern where `main()` runs only when the file is executed directly (`if __name__ == "__main__"`).  
- **Embeddable library:** Import the module and call `collect_sysinfo()`, `print_sysinfo()`, `write_sysinfo_csv()`, or `write_sysinfo_json()` from another script without running the CLI.

---

## Library usage (without CLI)

Other code can import functions without triggering the command-line interface:

```python
import sysinfo

data = sysinfo.collect_sysinfo()
sysinfo.print_sysinfo(data)
```

Run the CLI only when executing `sysinfo.py` as the main program.

---

## Behavioral notes

- **Primary IP:** The script opens a UDP socket toward `8.8.8.8` to discover which local address the kernel would use for outbound traffic. **No payload is sent** to Google; it is a common trick to read the chosen source IP. This needs **routing/network** to be up; odd VPN or firewall setups can affect the result.  
- **MAC address:** Resolved by matching that IP to an interface via `psutil`. If no match is found, the value may be missing or `None`.  
- **Top CPU processes:** Rankings use a **short delay** (`sleep`) so `cpu_percent` readings are meaningful; results are a snapshot, not a long-term average.

---

## License and version

See the header in `sysinfo.py`. This README reflects the script behavior as of the embedded version comment in that file.
