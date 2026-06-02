# Sprint 4 Script: `healthmon.py`

## Objectives

- Build a health monitoring script with **configurable thresholds**
- Use the Python **`logging`** module for all output (**no `print()`**)
- Write alerts to **syslog** when thresholds are breached
- Schedule automated checks with **cron**
- Write a well documented, followable **README**

---

## Inputs

| Usage | Command |
|-------|---------|
| Normal run | `python healthmon.py <config.json>` |
| Summary report | `python healthmon.py <config.json> --check` |

The config file defines thresholds and log file paths. See [Sample `config.json`](#sample-configjson) below.

---

## Outputs (Submission for Grading)

Submit via your **`sprint_scripts`** GitHub repo — **not** Canvas or email.

| Deliverable | Details |
|-------------|---------|
| Script | Valid Python file named `healthmon.py` |
| Config | `config.json` (paths adjusted for your machine) |
| Evidence | Log file content showing normal logging **and** syslog entries when alerts fire |
| Branch | `sprint4-healthmon` |
| README | Well documented, followable usage and setup guide |
| Canvas | Submit the **URL** to your `sprint4-healthmon` branch |

---

## What the Script Must Check

All thresholds come from the config file. **Nothing should be hardcoded.**

| Check | Source | Compare against |
|-------|--------|-----------------|
| Disk usage | Root filesystem (`/`) percent used | `checks.disk_usage_percent` |
| Memory usage | RAM percent used | `checks.memory_usage_percent` |
| CPU load | 1-minute load average | `checks.cpu_load_1min` |
| Services | At least 2 systemd services (e.g. `sshd`, `cron`) | `checks.services` list |

When a threshold is **breached**:

1. Log the alert via the Python `logging` module (main log file)
2. Write to a **separate alert log file** (`alert_log` in config)
3. Write to **syslog**

When all checks **pass**, log normal status messages only (no syslog/alert-log spam unless you choose to — focus alert channels on breaches).

---

## Sample `config.json`

Adjust paths for your machine (sample uses `/home/ubuntu/`; on this Pi you might use `/home/netpi/`):

```json
{
    "checks": {
        "disk_usage_percent": 80,
        "memory_usage_percent": 90,
        "cpu_load_1min": 2.0,
        "services": ["sshd", "cron"]
    },
    "log_file": "/home/netpi/healthmon.log",
    "alert_log": "/home/netpi/alerts.log"
}
```

---

## Code Hygiene Requirements

Follow the same standards as prior sprints (`sysinfo.py`, `netrecon.py`):

- **Shebang:** `#!/usr/bin/python3` at the top
- **No `print()`** — use `logging` for every message (info, warning, error)
- **Modular design:** One function per concern (load config, check disk, check memory, check CPU, check services, write alerts). Another script should be able to `import healthmon` without running the main loop unless executed directly (`if __name__ == "__main__":`)
- **Docstrings** on public functions
- **Graceful error handling:** Bad config, missing keys, invalid JSON, unreadable log paths, unknown services — tell the user **what to fix**, then exit with a non-zero code. Never fail silently or dump a raw traceback without context
- **Dependencies:** Prefer stdlib where possible (`json`, `logging`, `logging.handlers.SysLogHandler`, `argparse`, `subprocess`). `psutil` is a reasonable choice for disk/memory/load (you already used it in Sprint 2)
- **Lint clean:** Run `ruff check healthmon.py` before committing

---

## Recommended Project Layout

```
sprints_scripts/
├── healthmon.py       # main script
├── config.json        # thresholds and log paths
├── requirements.txt   # e.g. psutil (if used)
├── README.md          # user-facing documentation
└── instructions.md    # this file (assignment guide)
```

---

## Step-by-Step Build Guide

### 1. Create the branch

```bash
cd /home/netpi/projects/sprints_scripts
git checkout sprint4-healthmon   # or: git checkout -b sprint4-healthmon
```

### 2. Parse command-line arguments

Use `argparse`:

- **Positional:** `config` — path to JSON config file
- **Optional:** `--check` — print a human-readable summary report (still via logging, or log to stdout through a StreamHandler only for `--check` if graders expect terminal output; safest approach: configure logging with a console handler when `--check` is passed)

Validate early:

- Config file path exists and is readable
- File contains valid JSON
- Required keys present: `checks`, `log_file`, `alert_log`
- Inside `checks`: `disk_usage_percent`, `memory_usage_percent`, `cpu_load_1min`, `services` (non-empty list)

### 3. Set up logging

```python
import logging
from logging.handlers import SysLogHandler

# Main log → config["log_file"]  (FileHandler)
# Alerts   → config["alert_log"] (separate FileHandler, WARNING+ or dedicated alert logger)
# Syslog   → SysLogHandler (facility=LOG_DAEMON or LOG_USER)
```

Tips:

- Create log directories if needed, or fail with a clear message if the parent directory is not writable
- Use consistent format strings, e.g. `"%(asctime)s %(levelname)s %(message)s"`
- Use `logger.warning()` or `logger.error()` for threshold breaches

### 4. Implement each health check

**Disk usage (`/`)**

- `psutil.disk_usage("/").percent` or parse `df` output
- Alert if `percent >= checks["disk_usage_percent"]`

**Memory usage**

- `psutil.virtual_memory().percent`
- Alert if `percent >= checks["memory_usage_percent"]`

**CPU 1-minute load average**

- `os.getloadavg()[0]` (Linux) or read `/proc/loadavg`
- Alert if `load_1min >= checks["cpu_load_1min"]`

**Services**

- For each service name in `checks["services"]`, verify it is active:
  - `systemctl is-active --quiet <service>` via `subprocess.run`
  - Return code `0` = running; non-zero = not running → alert
- Handle invalid service names with a clear log message

Each check function should return a small result object or dict, e.g. `{"name": "disk", "value": 42.1, "threshold": 80, "ok": True}`.

### 5. `--check` summary report

When `--check` is passed, after running all checks, log a formatted summary:

```
=== Health Monitor Summary ===
Disk usage:     45.2%  (threshold 80%)   OK
Memory usage:   62.1%  (threshold 90%)   OK
CPU load (1m):  0.34   (threshold 2.0)   OK
Service sshd:   active                 OK
Service cron:   active                 OK
Overall:        HEALTHY
```

Mark `UNHEALTHY` if any check failed.

### 6. Alert pipeline

Centralize alert handling in one function, e.g. `send_alert(message)`:

1. Log to main logger at WARNING/ERROR
2. Append to `alert_log` file (via dedicated handler or explicit write)
3. Emit via `SysLogHandler` so entries appear in system logs

Verify syslog on Linux:

```bash
# After triggering an alert:
grep healthmon /var/log/syslog
# or on some systems:
journalctl -t healthmon --since "5 min ago"
```

Set the syslog ident/tag if needed: `SysLogHandler(ident="healthmon")`.

### 7. Main entry point

```python
def main():
    args = parse_args()
    config = load_config(args.config)
    setup_logging(config)
    results = run_all_checks(config)
    if args.check:
        log_summary(results)
    handle_alerts(results, config)

if __name__ == "__main__":
    main()
```

Exit with code `0` if healthy, `1` if any check failed (useful for cron/monitoring).

---

## Cron Setup

Run the script on a schedule without manual intervention.

1. Use absolute paths in crontab (cron does not load your shell profile)
2. Activate venv in the cron line if dependencies live in `.venv`

Example — every 5 minutes:

```bash
crontab -e
```

Add:

```cron
*/5 * * * * /home/netpi/projects/sprints_scripts/.venv/bin/python /home/netpi/projects/sprints_scripts/healthmon.py /home/netpi/projects/sprints_scripts/config.json >> /home/netpi/healthmon-cron.log 2>&1
```

Confirm cron is running:

```bash
systemctl status cron    # or crond on some distros
crontab -l
```

After a few minutes, inspect `healthmon.log` for scheduled entries.

---

## Testing Alerts

You must demonstrate that alerts reach **both** the alert log and **syslog**.

| Method | How |
|--------|-----|
| Lower a threshold | Temporarily set `disk_usage_percent` to `1` in `config.json`, run script, restore value |
| CPU stress | `stress-ng --cpu 2 --timeout 60s` (install if needed: `sudo apt install stress-ng`) |
| Stop a service | `sudo systemctl stop cron` → run script → `sudo systemctl start cron` |

Capture evidence for submission:

```bash
tail -20 /home/netpi/healthmon.log
tail -10 /home/netpi/alerts.log
grep healthmon /var/log/syslog | tail -5
```

Paste representative lines into your README or keep log snippets in the repo (optional `evidence/` folder — not required if README shows samples).

---

## Error Handling Checklist

Test these cases and confirm helpful messages (not silent failure):

| Bad input | Expected behavior |
|-----------|-------------------|
| Missing config argument | Usage/help message, exit non-zero |
| Config file not found | `"Config file not found: <path>"` |
| Invalid JSON | `"Invalid JSON in config: ..."` |
| Missing required key | `"Missing required key: checks.disk_usage_percent"` |
| Empty `services` list | `"services list must contain at least 2 service names"` |
| Unwritable log path | Clear permission/path error |
| Non-numeric threshold | `"disk_usage_percent must be a number"` |

---

## README Requirements

Your `README.md` should be written for someone who has never seen the script. Include:

1. **What it does** — one short paragraph
2. **Requirements** — Python version, OS (Linux), optional packages, systemd
3. **Installation** — venv + `pip install -r requirements.txt`
4. **Configuration** — explain each key in `config.json`
5. **Usage** — both normal run and `--check` with example commands
6. **Cron setup** — copy-paste crontab example with your paths
7. **Log files** — where to find main log, alert log, and syslog
8. **Testing alerts** — how you verified breaches (brief)
9. **Troubleshooting** — common issues (permissions, wrong service names, cron path)

Use the same thorough style as your Sprint 3 `netrecon.py` README (table of contents, examples, troubleshooting section).

---

## Git Submission Workflow

```bash
# From repo root on branch sprint4-healthmon
git add healthmon.py config.json requirements.txt README.md
git status
git commit -m "Add healthmon.py with config, logging, syslog alerts, and cron docs"
git push -u origin sprint4-healthmon
```

**Canvas submission:** paste the branch URL, e.g.

`https://github.com/<your-username>/sprint_scripts/tree/sprint4-healthmon`

---

## Pre-Submission Checklist

- [ ] `healthmon.py` runs: `python healthmon.py config.json`
- [ ] `--check` prints/logs a readable summary
- [ ] All four check types implemented (disk, memory, CPU load, ≥2 services)
- [ ] All thresholds read from config — no hardcoded limits
- [ ] No `print()` anywhere in the script
- [ ] Threshold breach → main log + alert log + syslog
- [ ] Bad config / missing args handled with clear messages
- [ ] Cron entry documented and tested
- [ ] `config.json` committed (with paths valid for grader or documented how to change)
- [ ] README complete and followable
- [ ] Code pushed to `sprint4-healthmon` branch
- [ ] Canvas: branch URL submitted

---

## Quick Reference: Python Modules

| Module | Purpose |
|--------|---------|
| `argparse` | CLI: config path + `--check` |
| `json` | Load config file |
| `logging` | All script output |
| `logging.handlers.SysLogHandler` | Syslog alerts |
| `subprocess` | `systemctl is-active` for services |
| `psutil` (optional) | Disk, memory stats |
| `os` | `getloadavg()` for CPU load |

---

## Notes from Assignment

- Service names must match what `systemctl` expects on your distro (`ssh` vs `sshd`, `cron` vs `crond` — verify with `systemctl list-units --type=service`)
- Do not submit the script on Canvas; only the GitHub branch link
- Restart any service you stop during testing (`cron`, etc.)
- Keep alert thresholds realistic in the committed `config.json`; use temporary edits only for testing
