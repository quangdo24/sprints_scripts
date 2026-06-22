# Sprints Scripts by Quang Do

BAS Cybersecurity Automation course scripts.

This README covers **Sprint 5 (Ansible)**: deploying `healthmon.py` from Sprint 4 onto **linux2** using two idempotent playbooks.

---

## Sprint 5 Overview

| Playbook | Purpose |
|----------|---------|
| `configure.yml` | Prepare linux2: packages, Python deps, directories |
| `deploy.yml` | Copy `healthmon.py` + `config.json`, schedule cron, verify |

**Control node:** linux1 — where you run `ansible-playbook`  
**Managed node:** linux2 — receives healthmon

---

## Prerequisites

### 1. Two AWS EC2 instances (from the setup lab)

| Host | Role | Connection |
|------|------|------------|
| **linux1** | Ansible control node | `ansible_connection=local` |
| **linux2** | Managed server | SSH as `ubuntu` |

### 2. SSH key access

linux1 must SSH into linux2 without a password prompt. Your public key (`~/.ssh/id_ed25519.pub`) must be in linux2's `~/.ssh/authorized_keys`.

Test connectivity:

```bash
ansible all -i inventory.ini -m ping
```

Expected: `SUCCESS` with `"ping": "pong"` for both hosts.

### 3. Ansible installed on linux1

```bash
sudo apt update
sudo apt install -y ansible
ansible --version
```

---

## Inventory (`inventory.ini`)

```ini
[servers]
linux1 ansible_host=enter-ip-linux1 ansible_connection=local
linux2 ansible_host=enter-ip-linux2 ansible_user=ubuntu

[servers:vars]
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

Replace `enter-ip-linux1` and `enter-ip-linux2` with each host's public or private IP (or a resolvable hostname).

| Variable | Meaning |
|----------|---------|
| `ansible_host` | IP or hostname Ansible uses to reach the host |
| `ansible_connection=local` | Run tasks on linux1 without SSH |
| `ansible_user` | SSH username on linux2 |
| `ansible_ssh_private_key_file` | Private key for SSH to linux2 |

Update `ansible_host` in `inventory.ini` if linux1 or linux2 addresses change after an instance stop/start.

---

## What Gets Deployed

On **linux2**, files land in `/home/ubuntu/projects/sprints_scripts/`:

```
/home/ubuntu/projects/sprints_scripts/
├── healthmon.py          # Sprint 4 health monitor script
├── config.json           # Thresholds and log paths
└── evidence/
    ├── healthmon.log     # Normal status log (created on first run)
    ├── alerts.log        # Alert log (created when thresholds breach)
    └── healthmon-cron.log # Cron stdout/stderr
```

`config.json` paths point at the `evidence/` directory above.

---

## Playbook Details

### `configure.yml` — system configuration

Runs on **linux2** with `become: true` (sudo). Tasks:

1. Refresh apt cache
2. Install `python3`, `python3-pip`, and `cron`
3. Ensure the `cron` service is running
4. Install `python3-psutil` via apt (required by `healthmon.py`)
5. Create project and evidence directories

### `deploy.yml` — script deployment

Runs on **linux2** as `ubuntu`. Tasks:

1. Copy `healthmon.py` (mode `0755`)
2. Copy `config.json` (mode `0644`)
3. Add a cron job to run healthmon every 5 minutes
4. Run `healthmon.py config.json --check` to verify deployment

---

## How to Run

From the `sprints_scripts` directory on **linux1**:

```bash
cd ~/sprints_scripts

# Step 1: Configure the system
ansible-playbook -i inventory.ini configure.yml

# Step 2: Deploy the script
ansible-playbook -i inventory.ini deploy.yml
```

---

## Verify on linux2

SSH into linux2 and confirm:

```bash
ssh ubuntu@linux2

# Files deployed
ls -la ~/projects/sprints_scripts/

# Manual test run
python3 ~/projects/sprints_scripts/healthmon.py ~/projects/sprints_scripts/config.json --check

# Cron job present
crontab -l

# Logs after a run
ls ~/projects/sprints_scripts/evidence/
```

---
