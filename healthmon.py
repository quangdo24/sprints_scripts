#!/usr/bin/python3
# healthmon.py: Monitor disk, memory, CPU load, and systemd services against
# thresholds from a config file. Logs normal status and raises alerts (main log,
# alert log, and syslog) when a threshold is breached.
# Licensed under the MIT License (https://opensource.org/license/mit)
# QuangDo-20260606: V1.0.0
import argparse
import json
import logging
import os
import subprocess
import sys
from logging.handlers import SysLogHandler
import psutil

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

# Loggers are wired up in setup_logging(). The main logger holds the normal
# status messages; the alert logger fans out breaches to the alert file + syslog.
log = logging.getLogger("healthmon")
alert_log = logging.getLogger("healthmon.alerts")


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
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        metavar="MINUTES",
        help="Minutes between runs for --install-cron (default: 5)",
    )
    cron = parser.add_mutually_exclusive_group()
    cron.add_argument(
        "--install-cron",
        action="store_true",
        help="Schedule this script to run on a timer via the user's crontab",
    )
    cron.add_argument(
        "--remove-cron",
        action="store_true",
        help="Remove the scheduled healthmon cron job",
    )
    return parser.parse_args()


def fail(message):
    """Report a fatal problem to the user and exit with a non-zero code."""
    logging.error(message)
    sys.exit(1)


def load_config(path):
    """Load and validate the JSON config file, returning it as a dict."""
    if not os.path.isfile(path):
        fail(f"Config file not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in config: {e}")
    except OSError as e:
        fail(f"Could not read config file: {e}")

    for key in ("checks", "log_file", "alert_log"):
        if key not in config:
            fail(f"Missing required key: {key}")

    checks = config["checks"]
    numeric_keys = ("disk_usage_percent", "memory_usage_percent", "cpu_load_1min")
    for key in numeric_keys:
        if key not in checks:
            fail(f"Missing required key: checks.{key}")
        if not isinstance(checks[key], (int, float)):
            fail(f"{key} must be a number")

    services = checks.get("services")
    if not isinstance(services, list) or len(services) < 2:
        fail("services list must contain at least 2 service names")

    return config


def setup_logging(config, console):
    """Attach file, alert-file, and syslog handlers to the loggers."""
    formatter = logging.Formatter(LOG_FORMAT)

    log.setLevel(logging.INFO)
    alert_log.setLevel(logging.WARNING)
    # Alerts get handled explicitly, so don't let them bubble into the main log twice.
    alert_log.propagate = False

    try:
        main_handler = logging.FileHandler(config["log_file"])
    except OSError as e:
        fail(f"Cannot open log file {config['log_file']}: {e}")
    main_handler.setFormatter(formatter)
    log.addHandler(main_handler)

    try:
        alert_handler = logging.FileHandler(config["alert_log"])
    except OSError as e:
        fail(f"Cannot open alert log {config['alert_log']}: {e}")
    alert_handler.setFormatter(formatter)
    alert_log.addHandler(alert_handler)

    try:
        syslog_handler = SysLogHandler(address="/dev/log")
        syslog_handler.setFormatter(logging.Formatter("healthmon: %(levelname)s %(message)s"))
        alert_log.addHandler(syslog_handler)
    except OSError as e:
        # Syslog is best-effort; keep going with file logging if the socket is missing.
        log.warning(f"Could not connect to syslog: {e}")

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)


def setup_console(level=logging.INFO):
    """Send log messages to stdout (used for cron management and --check)."""
    log.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log.addHandler(handler)


# Trailing tag so we can find and replace our own crontab line later.
CRON_TAG = "# healthmon"


def read_crontab():
    """Return the current user's crontab as a list of lines (empty if none)."""
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        fail("crontab command not found; cannot manage scheduled jobs.")
    if result.returncode != 0:
        # A missing crontab is normal for a fresh user; treat it as empty.
        return []
    return result.stdout.splitlines()


def write_crontab(lines):
    """Replace the user's crontab with the given list of lines."""
    text = "\n".join(lines) + "\n" if lines else ""
    proc = subprocess.run(["crontab", "-"], input=text, text=True, check=False)
    if proc.returncode != 0:
        fail("Failed to update crontab.")


def install_cron(config_path, config, interval):
    """Add or update a crontab entry that runs this script every `interval` minutes."""
    if interval < 1:
        fail("--interval must be a positive number of minutes")

    python_exe = sys.executable
    script = os.path.abspath(__file__)
    config_abs = os.path.abspath(config_path)
    cron_log = os.path.join(
        os.path.dirname(os.path.abspath(config["log_file"])), "healthmon-cron.log"
    )
    cron_line = (
        f"*/{interval} * * * * {python_exe} {script} {config_abs} "
        f">> {cron_log} 2>&1  {CRON_TAG}"
    )

    lines = [ln for ln in read_crontab() if CRON_TAG not in ln]
    lines.append(cron_line)
    write_crontab(lines)
    log.info(f"Scheduled healthmon to run every {interval} minute(s).")
    log.info(f"Cron line: {cron_line}")
    log.info("Verify with: crontab -l")


def remove_cron():
    """Remove the healthmon entry from the user's crontab, if present."""
    lines = read_crontab()
    kept = [ln for ln in lines if CRON_TAG not in ln]
    if len(kept) == len(lines):
        log.info("No healthmon cron job found; nothing to remove.")
        return
    write_crontab(kept)
    log.info("Removed the healthmon cron job.")


def send_alert(message):
    """Raise an alert to the main log, the alert log, and syslog."""
    log.warning(message)
    alert_log.warning(message)


def check_disk(threshold):
    """Check root filesystem usage against the disk threshold."""
    value = psutil.disk_usage("/").percent
    return {
        "name": "Disk usage",
        "display": f"{value:.1f}%",
        "threshold": f"{threshold}%",
        "ok": value < threshold,
    }


def check_memory(threshold):
    """Check RAM usage against the memory threshold."""
    value = psutil.virtual_memory().percent
    return {
        "name": "Memory usage",
        "display": f"{value:.1f}%",
        "threshold": f"{threshold}%",
        "ok": value < threshold,
    }


def check_cpu(threshold):
    """Check the 1-minute load average against the CPU threshold."""
    value = os.getloadavg()[0]
    return {
        "name": "CPU load (1m)",
        "display": f"{value:.2f}",
        "threshold": f"{threshold}",
        "ok": value < threshold,
    }


def check_services(services):
    """Check that each systemd service is active, one result per service."""
    results = []
    for service in services:
        try:
            rc = subprocess.run(
                ["systemctl", "is-active", "--quiet", service],
                check=False,
            ).returncode
        except FileNotFoundError:
            fail("systemctl not found; this script needs a systemd-based Linux.")
        results.append({
            "name": f"Service {service}",
            "display": "active" if rc == 0 else "inactive",
            "threshold": "active",
            "ok": rc == 0,
        })
    return results


def run_all_checks(config):
    """Run every configured check and return a list of result dicts."""
    checks = config["checks"]
    results = [
        check_disk(checks["disk_usage_percent"]),
        check_memory(checks["memory_usage_percent"]),
        check_cpu(checks["cpu_load_1min"]),
    ]
    results.extend(check_services(checks["services"]))
    return results


def handle_results(results):
    """Log normal status for passing checks and raise alerts for breaches."""
    for result in results:
        if result["ok"]:
            log.info(f"{result['name']} OK: {result['display']} (threshold {result['threshold']})")
        else:
            send_alert(
                f"{result['name']} breached threshold: "
                f"{result['display']} (threshold {result['threshold']})"
            )


def log_summary(results):
    """Log a human-readable summary report of all checks."""
    lines = ["=== Health Monitor Summary ==="]
    for result in results:
        status = "OK" if result["ok"] else "ALERT"
        value = f"{result['display']} (threshold {result['threshold']})"
        lines.append(f"{result['name']:<16}{value:<32}{status}")
    healthy = all(result["ok"] for result in results)
    lines.append(f"{'Overall:':<16}{'HEALTHY' if healthy else 'UNHEALTHY'}")
    log.info("\n".join(lines))


def main():
    """Load config, run health checks, and report status and alerts."""
    args = parse_args()
    config = load_config(args.config)

    # Cron management is a one-shot action that reports to the terminal, not
    # the monitoring log files, so handle it before the normal logging setup.
    if args.install_cron:
        setup_console()
        install_cron(args.config, config, args.interval)
        return
    if args.remove_cron:
        setup_console()
        remove_cron()
        return

    setup_logging(config, console=args.check)

    results = run_all_checks(config)
    handle_results(results)
    if args.check:
        log_summary(results)

    healthy = all(result["ok"] for result in results)
    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()