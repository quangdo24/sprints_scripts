# Sprints Scripts

---

## `logparser.py`

**What it does:** Reads a system log file (for example Linux `auth.log`), finds lines that report **failed SSH password** attempts, and saves **timestamp**, **username**, and **source IP** to a CSV file. It also prints each match to the terminal.

**Requirements:** Python 3. No extra packages—only the standard library (`sys`, `re`, `csv`).

### How to run

From this folder:

```bash
python3 logparser.py <path-to-log-file> <output.csv>
```

You must pass **exactly two** arguments:

| Argument | Meaning |
|----------|---------|
| 1st | Path to the log file to read |
| 2nd | Path to the CSV file to create (or overwrite) |

If you omit arguments or pass the wrong count, the script prints usage and exits with code `1`.

### Example

```bash
python3 logparser.py /var/log/auth.log ssh_failures.csv
```

*(Reading `/var/log/auth.log` usually needs root or appropriate permissions on your system.)*

### What gets matched

The script looks for log lines similar to:

- `Failed password for alice from 203.0.113.10`
- `Failed password for invalid user bob from 198.51.100.5`

The first column in the log line is treated as the **timestamp** (for example `Apr 13 14:22:01` style text, depending on your log format).

### CSV output

The output file has a header row and one row per match:

| Column | Description |
|--------|-------------|
| `Timestamp` | The date/time fragment from the start of the matching log line |
| `Username` | The account name (including names after `invalid user`) |
| `IP Address` | The IPv4 address the attempt came from |

When it finishes, the script prints how many failed attempts were found and written.

### Errors

- If the **log file** does not exist or cannot be opened, you’ll see an error message and the script exits with code `1`.
- If the **output path** cannot be opened for writing, you’ll see an error and the script exits with code `1`.

### Use as a module

The file defines `parse_log(log_file, output_file)`. You can import it from another Python script and call `parse_log(...)` if you need the same behavior programmatically.

---

**Author:** Quang Do · **Script version:** 1.0.0
