# Script 2: sysinfo.py

Make sure you use the code hygiene expected for this course.

## Objectives

- Use Python system modules to gather information about a Linux server
- Output data in multiple formats based on a command line argument
- Write code that works as both a standalone script and an importable module

## Inputs

- Script takes one argument on the command line: `sysinfo.py <screen|csv|json>`
- Run on your AWS Linux instance

## Outputs

- A valid Python script named sysinfo.py submitted via PR to your individual repo
- If csv: a file named sysinfo.csv in the same directory
- If json: a file named sysinfo.json in the same directory
- Branch: `sprint2-sysinfo`

## Notes

- The script collects the following information from the local machine:
  - Hostname
  - OS type and version
  - Kernel version
  - CPU count
  - Total RAM (GB)
  - Disk total and free space (GB) for the root partition
  - Primary IP address
  - Primary MAC address
  - Uptime
  - Top 5 processes by CPU usage
- With `screen` argument: display all info to the console in a readable format
- With `csv` argument: write to sysinfo.csv (do not display on the screen)
- With `json` argument: write to sysinfo.json (do not display on the screen)
- With no argument or an invalid argument: print a usage message
- The best approach is to use `subprocess.run` for some data and `psutil`/`platform` for others. You will need to install psutil via pip.
- Use a separate function for each piece of information. Another script should be able to do `import sysinfo` and call `sysinfo.get_hostname()` without triggering the main program. We will be reusing this as a library in future assignments.
- All code hygiene standards apply.

## Example Screen Output

    ==================================================
      SYSTEM INFORMATION REPORT
    ==================================================

      Hostname             linux1
      Os Type              Linux
      Os Version           #45-Ubuntu SMP ...
      Kernel               6.8.0-45-generic
      Cpu Count            2
      Ram Gb               1.0
      Disk Total Gb        8.0
      Disk Free Gb         5.2
      Primary Ip           172.31.57.234
      Primary Mac          06:a5:d1:bf:d7:f9
      Uptime               up 3 days, 4 hours, 22 minutes

      Top 5 Processes by CPU:
      PID        CPU%     Name
      ----------------------------------------
      1234       12.3     python3
      567        8.1      sshd
      ...
