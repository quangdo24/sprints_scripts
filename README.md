# Sprints Scripts by Quang Do

BAS Cybersecurity Automation course scripts.

This README covers **Sprint 5 (Ansible)**: deploying `healthmon.py` from Sprint 4 onto **linux2** using two idempotent playbooks.

---

## Sprint 5 Overview

| Playbook | Purpose |
|----------|---------|
| `configure.yml` | Prepare linux2: packages, Python deps, directories |
| `deploy.yml` | Copy `healthmon.py` + `config.json`, schedule cron, verify |

**Control node:** linux1 (`ip-172-31-70-29`) — where you run `ansible-playbook`  
**Managed node:** linux2 (`52.0.222.192`) — receives healthmon

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
linux1 ansible_host=3.221.66.131 ansible_connection=local
linux2 ansible_host=52.0.222.192 ansible_user=ubuntu

[servers:vars]
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

| Variable | Meaning |
|----------|---------|
| `ansible_host` | IP address Ansible uses to reach the host |
| `ansible_connection=local` | Run tasks on linux1 without SSH |
| `ansible_user` | SSH username on linux2 |
| `ansible_ssh_private_key_file` | Private key for SSH to linux2 |

Update `ansible_host` values if your public IPs change after an instance stop/start.

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

## Idempotency Demonstration

Ansible playbooks should be **idempotent**: running them again makes no changes if the system is already in the desired state.

Run each playbook **twice** and compare the summary line:

```bash
ansible-playbook -i inventory.ini configure.yml
ansible-playbook -i inventory.ini configure.yml   # second run

ansible-playbook -i inventory.ini deploy.yml
ansible-playbook -i inventory.ini deploy.yml      # second run
```

**First run** — expect tasks with `changed=1` (packages installed, files copied, cron added).

**Second run** — expect **`changed=0`** on all tasks:

```text
PLAY RECAP *********************************************************************
linux2   : ok=6    changed=0    unreachable=0    failed=0    skipped=0    ...
```

That `changed=0` on the second run is your idempotency evidence.

---

## Verify on linux2

SSH into linux2 and confirm:

```bash
ssh ubuntu@52.0.222.192

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

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Permission denied (publickey)` | Add linux1's public key to linux2 `authorized_keys` |
| `UNREACHABLE` on linux2 | Check security group allows SSH (port 22) from linux1 |
| `Could not open log file` | Run `configure.yml` first to create the evidence directory |
| `No module named psutil` | Re-run `configure.yml` (installs `python3-psutil`) |
| Stale IP in inventory | Update `ansible_host` in `inventory.ini` after instance restart |

---

## Submission Checklist (Sprint 5)

| Deliverable | File |
|-------------|------|
| Inventory | `inventory.ini` |
| System configuration playbook | `configure.yml` |
| Script deployment playbook | `deploy.yml` |
| Health monitor script | `healthmon.py` |
| Config file | `config.json` |
| Idempotency evidence | Second playbook run showing `changed=0` |
| Documentation | This README |
| Branch | `sprint5-ansible` |

---

## Related Sprints

- **Sprint 4:** `healthmon.py` — disk, memory, CPU, and service monitoring with configurable thresholds
- **Setup lab:** Two AWS EC2 instances, SSH keys, Tailscale optional
