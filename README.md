# Sprints Scripts by Quang Do

BAS Cybersecurity Automation course scripts.

This repository holds coursework across multiple **sprint branches**. Each branch is a self-contained sprint with its own scripts, docs, and (where needed) dependencies. Checkout a branch to run that sprint’s work:

```bash
git checkout <branch-name>
```

---

## Branch overview

| Branch | Focus | Main artifact |
|--------|--------|----------------|
| [`sprint1-logparser`](#sprint1-logparser) | Parse failed SSH logins from auth logs | `logparser.py` |
| [`sprint2-sysinfo`](#sprint2-sysinfo) | Collect local system inventory | `sysinfo.py` |
| [`sprint3-netrecon`](#sprint3-netrecon) | Network recon (Nmap + geolocation) | `netrecon.py` |
| [`sprint4-healthmon`](#sprint4-healthmon) | Host health checks + alerting | `healthmon.py` |
| [`sprint5-ansible`](#sprint5-ansible) | Deploy healthmon with Ansible | `configure.yml`, `deploy.yml` |

---

## `sprint1-logparser`

**Goal:** Detect failed SSH password attempts in a system auth log and export them to CSV.

| Item | Detail |
|------|--------|
| Script | `logparser.py` |
| Dependencies | Python 3 standard library only (`sys`, `re`, `csv`) |
| Sample output | `invalid-auth-output.csv` |

**Behavior:** Reads a log file (e.g. Linux `auth.log`), matches lines like `Failed password for … from …`, and writes **Timestamp**, **Username**, and **IP Address** to a CSV while printing matches to the terminal.

```bash
python3 logparser.py <path-to-log-file> <output.csv>
```

---

## `sprint2-sysinfo`

**Goal:** Sample the host and report identity, OS, CPU, memory, disk, network, uptime, and top processes.

| Item | Detail |
|------|--------|
| Script | `sysinfo.py` |
| Dependencies | `psutil`, `py-cpuinfo` (`requirements.txt`) |
| Outputs | Terminal (`-s`), `sysinfo.csv` (`-c`), or `sysinfo.json` (`-j`) |

**Platform:** Linux-first (Unix-like / macOS generally OK; Windows not the design target).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 sysinfo.py -s    # screen
python3 sysinfo.py -c    # CSV
python3 sysinfo.py -j    # JSON
```

---

## `sprint3-netrecon`

**Goal:** Recon a target IP with **Nmap** (open ports / services) and **ip-api.com** (geo / ISP), then print a summary and write CSV.

| Item | Detail |
|------|--------|
| Script | `netrecon.py` |
| Dependencies | System **Nmap** + `python-nmap`, `requests` |
| Notes | Full TCP scan (`-p-`) can take a long time |

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 netrecon.py <target_ip> <output.csv>
```

**Use only on systems you own or have explicit permission to scan.**

---

## `sprint4-healthmon`

**Goal:** Check disk, memory, CPU load, and systemd services against thresholds in `config.json`. Passes go to the main log; breaches also go to an alert log and syslog. Optional cron scheduling.

| Item | Detail |
|------|--------|
| Script | `healthmon.py` |
| Config | `config.json` (thresholds, log paths, service names) |
| Evidence | `evidence/healthmon.log`, `evidence/alerts.log`, etc. |
| Platform | Linux with **systemd** |

```bash
python3 healthmon.py config.json           # log only
python3 healthmon.py config.json --check   # + terminal summary
python3 healthmon.py config.json --install-cron   # every 5 min
```

Exit code `0` = healthy, `1` = one or more checks failed.

---

## `sprint5-ansible`

**Goal:** Deploy Sprint 4’s `healthmon.py` to a managed host with idempotent Ansible playbooks.

| Item | Detail |
|------|--------|
| Playbooks | `configure.yml` (packages, dirs, deps), `deploy.yml` (copy files, cron, verify) |
| Inventory | `inventory.ini` — **linux1** (control, local) and **linux2** (managed via SSH) |
| Also includes | `healthmon.py`, `config.json`, screenshots |

Typical flow on the control node:

```bash
ansible all -i inventory.ini -m ping
ansible-playbook -i inventory.ini configure.yml
ansible-playbook -i inventory.ini deploy.yml
```

Update host IPs and the SSH key path in `inventory.ini` before running.

---

## How the sprints connect

1. **Sprint 1–3** build standalone Python automation skills (logs, local inventory, network recon).
2. **Sprint 4** adds continuous host monitoring and alerting.
3. **Sprint 5** packages that monitor for remote deployment with Ansible.

---

**Author:** Quang Do  
**Course:** BAS Cybersecurity Automation
