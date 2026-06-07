# Health Monitor (`healthmon.py`)

`healthmon.py` checks disk, memory, CPU load, and systemd services against thresholds in a
config file. Passing checks are logged normally; breaches go to the main log, an alert log, and
syslog.

---

## Quick start

Run these steps from the project folder (the directory that contains `healthmon.py`).

### 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Edit `config.json` for your machine

Open `config.json` and update **`log_file`**, **`alert_log`**, and **`services`** for your
system. Use **absolute paths** for the log files (required for cron).

Example — replace `/path/to/sprints_scripts` with where you cloned this repo:

```json
{
    "checks": {
        "disk_usage_percent": 80,
        "memory_usage_percent": 90,
        "cpu_load_1min": 2.0,
        "services": ["sshd", "cron"]
    },
    "log_file": "/path/to/sprints_scripts/evidence/healthmon.log",
    "alert_log": "/path/to/sprints_scripts/evidence/alerts.log"
}
```

Tip — print your project path:

```bash
pwd
# example output: /home/you/projects/sprints_scripts
```

Service names must match your distro (`sshd` vs `ssh`, `cron` vs `crond`). List them with:

```bash
systemctl list-units --type=service
```

Make sure the `evidence/` folder exists (it ships with the repo).

### 3. Run a health check

**Normal run** — logs to files and syslog, no terminal output:

```bash
python healthmon.py config.json
```

**Summary on screen** — same checks, plus a readable report:

```bash
python healthmon.py config.json --check
```

Example output:

```
=== Health Monitor Summary ===
Disk usage      45.2% (threshold 80%)           OK
Memory usage    62.1% (threshold 90%)           OK
CPU load (1m)   0.34 (threshold 2.0)            OK
Service sshd    active (threshold active)       OK
Service cron    active (threshold active)       OK
Overall:        HEALTHY
```

Exit code is `0` when healthy, `1` when any check failed.

### 4. Schedule with cron (optional)

Let the script install its own crontab entry (uses absolute paths automatically):

```bash
python healthmon.py config.json --install-cron               # every 5 minutes
python healthmon.py config.json --install-cron --interval 10 # custom interval
python healthmon.py config.json --remove-cron                # unschedule
```

Verify:

```bash
crontab -l
tail -20 evidence/healthmon.log
```

See [Cron setup](#cron-setup) for manual crontab instructions.

---

## Table of contents

- [Quick start](#quick-start)
- [What this tool does](#what-this-tool-does)
- [Requirements](#requirements)
- [Configuration reference](#configuration-reference)
- [Log files](#log-files)
- [Cron setup](#cron-setup)
- [Testing alerts](#testing-alerts)
- [How the script works](#how-the-script-works)
- [Troubleshooting](#troubleshooting)

---

## What this tool does

When you run `python healthmon.py config.json`, the program will:

1. Load and validate `config.json`.
2. Set up logging to the main log file, alert log file, and syslog.
3. Run all four checks (disk, memory, CPU load, services).
4. Log a normal status line for every check that passes.
5. Raise an alert (main log + alert log + syslog) for every check that fails.
6. Exit with code `0` if everything is healthy, or `1` if any check failed.

Add `--check` to also print a readable summary report to the terminal.

---

## Requirements

| Requirement          | Details                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------- |
| **Operating system** | Linux with **systemd** (service checks use `systemctl`).                                      |
| **Python**           | 3.8 or newer (`python3 --version`).                                                           |
| **psutil**           | Disk and memory stats — installed via `requirements.txt`.                                     |
| **syslog**           | A system logger listening on `/dev/log` (`systemd-journald` or `rsyslog`). Standard on Linux. |

Everything else (`json`, `logging`, `argparse`, `subprocess`, `os`) is in the Python standard library.

---

## Configuration reference

All thresholds and paths live in `config.json` — nothing is hardcoded in the script.

| Key                           | Meaning                                                            |
| ----------------------------- | ------------------------------------------------------------------ |
| `checks.disk_usage_percent`   | Alert if root (`/`) usage reaches or exceeds this percent.         |
| `checks.memory_usage_percent` | Alert if RAM usage reaches or exceeds this percent.                |
| `checks.cpu_load_1min`        | Alert if the 1-minute load average reaches or exceeds this number. |
| `checks.services`             | List of systemd service names to verify (at least 2 required).     |
| `log_file`                    | Absolute path to the main log file.                                |
| `alert_log`                   | Absolute path to the alert-only log file.                          |

**Before your first run**, set `log_file` and `alert_log` to valid absolute paths on your
machine. The committed `config.json` may contain paths from the author's system — change them
to match yours (typically `…/evidence/healthmon.log` and `…/evidence/alerts.log` inside this
repo).

---

## Log files

| Destination   | What goes there                               | Location                          |
| ------------- | --------------------------------------------- | --------------------------------- |
| **Main log**  | Every check result — normal status and alerts | `log_file` in config (e.g. `evidence/healthmon.log`) |
| **Alert log** | Threshold breaches only                       | `alert_log` in config (e.g. `evidence/alerts.log`)   |
| **Cron log**  | stdout/stderr from scheduled runs             | `evidence/healthmon-cron.log` (next to main log)   |
| **Syslog**    | Threshold breaches only, tagged `healthmon`   | system journal (`journalctl`)     |

Inspect logs:

```bash
tail -20 evidence/healthmon.log
tail -10 evidence/alerts.log
journalctl -t healthmon --since "5 min ago"
```

Syslog is not written to a file in the repo. To keep a sample for submission, paste journal
output into `evidence/syslog.txt`:

```bash
journalctl -t healthmon --since "10 min ago" > evidence/syslog.txt
```

---

## Cron setup

### Option A — let the script schedule itself (recommended)

```bash
python healthmon.py config.json --install-cron
python healthmon.py config.json --install-cron --interval 10   # custom interval
python healthmon.py config.json --remove-cron                  # unschedule
```

The script builds the cron line with absolute paths to your Python, script, and config
automatically. Re-running `--install-cron` replaces the old entry instead of duplicating it.
Cron stdout/stderr goes to `healthmon-cron.log` in the same directory as `log_file`.

### Option B — add the crontab line manually

Cron does not load your shell profile — use **absolute paths** everywhere.

```bash
crontab -e
```

Add (replace paths with yours — use `which python` inside your activated venv):

```cron
*/5 * * * * /path/to/sprints_scripts/.venv/bin/python /path/to/sprints_scripts/healthmon.py /path/to/sprints_scripts/config.json >> /path/to/sprints_scripts/evidence/healthmon-cron.log 2>&1
```

Confirm:

```bash
systemctl status cron
crontab -l
```

---

## Testing alerts

Temporarily breach a threshold to prove alerts reach the alert log and syslog:

```bash
cp config.json /tmp/test.json
# edit /tmp/test.json -> set "disk_usage_percent": 1
python healthmon.py /tmp/test.json --check
```

Keep the same `log_file` and `alert_log` paths in the test copy so output still lands in
`evidence/`.

Check results:

```bash
tail -5 evidence/alerts.log
journalctl -t healthmon --since "5 min ago"
```

Other ways to trigger breaches:

- **CPU stress:** `stress-ng --cpu 2 --timeout 60s`
- **Stop a service:** `sudo systemctl stop cron` → run script → `sudo systemctl start cron`

Restore thresholds and restart any service you stopped when done.

---

## How the script works

The code is split into one function per concern and can be imported as a module without running
checks (`if __name__ == "__main__"` guards the entry point).

| Function                                    | Responsibility                                               |
| ------------------------------------------- | ------------------------------------------------------------ |
| `parse_args`                                | Read config path and optional flags (`--check`, cron flags). |
| `load_config`                               | Read JSON and validate required keys and types.              |
| `setup_logging`                             | Attach main file, alert file, and syslog handlers.           |
| `check_disk` / `check_memory` / `check_cpu` | Read one metric and compare to its threshold.                |
| `check_services`                            | Run `systemctl is-active` for each service.                  |
| `run_all_checks`                            | Run every check and collect results.                         |
| `handle_results`                            | Log normal status or call `send_alert` on a breach.          |
| `send_alert`                                | Fan a breach out to main log, alert log, and syslog.         |
| `log_summary`                               | Build the `--check` summary report.                          |
| `install_cron` / `remove_cron`              | Add, update, or remove the crontab entry.                    |

---

## Troubleshooting

| Problem                                               | Fix                                                                                                      |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `Config file not found`                               | Pass a valid path: `python healthmon.py config.json`                                                     |
| `Invalid JSON in config`                              | Check for trailing commas, missing quotes, etc.                                                          |
| `Missing required key: ...`                           | Add the key named in the error message.                                                                  |
| `services list must contain at least 2 service names` | Add at least two services to `checks.services`.                                                          |
| `Cannot open log file ...`                            | Set `log_file` / `alert_log` to absolute paths; parent directory must exist and be writable.             |
| A service always shows `inactive`                     | Wrong service name for your distro — run `systemctl list-units --type=service`.                          |
| Nothing in syslog                                     | Confirm `/dev/log` exists; file logging still works without syslog.                                        |
| Cron run does nothing                                 | Use absolute paths in crontab; check `evidence/healthmon-cron.log`.                                      |
| Logs go to the wrong place                            | You may be passing a different config file — check which file you pass on the command line.              |
