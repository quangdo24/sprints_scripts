net@rer# Project: Network Reconnaissance Tool

## Objectives
* **Scan Targets:** Use `python-nmap` to scan a target for open ports.
* **API Integration:** Use the `requests` library to query a public API.
* **Data Aggregation:** Combine data from multiple sources into one output.
* **Documentation:** Write a well-documented, followable README.

---

## Inputs
* **Command:** `python netrecon.py <target_ip> <output.csv>`
* **Targets:** Your own AWS box, localhost, or a classmate's box (with permission).

---

## Outputs (Submission for Grading)
* **Script:** A valid Python script named `netrecon.py` submitted via git.
* **CSV:** The output file submitted alongside the script.
* **Repository Details:**
    * **Repo:** `sprint_scripts`
    * **Branch:** `sprint3-netrecon`
* **README:** A well-documented README file.

---

## Technical Requirements & Notes

### Core Functionality
1. **Nmap Scanning:** Scan the target IP for open ports. For each open port, record the **port number**, **service name**, and **state**.
2. **Geolocation:** Query a public API (like [ip-api.com](http://ip-api.com)) to get the target's **country**, **region**, **city**, and **ISP**.
3. **Reporting:** Display a summary to the screen and write all results to the specified CSV file.

### Implementation Details
* **Dependencies:** You must install the appropriate Python modules and system packages.
* **Parsing:** Nmap returns nested dictionary structures. Iterate through them carefully. **Test on localhost first.**
* **Error Handling:** Handle bad input or failures gracefully. The script should prompt the user to fix inputs rather than throwing unhelpful errors or failing silently.

---

## Extra Credit
* Add an optional `--remote <ip>` flag that uses **Paramiko** to SSH into a remote host.