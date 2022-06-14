# iperf_early_stopping

## Introduction

This Python script allows you to run iperf2 until a specified bandwidth is reached.

## How to run

First, clone the repository:

```bash
git clone https://github.com/SMU-ATT-Center-for-Virtualization/iperf_early_stopping
```

Then, run the following command:

```bash
cd iperf_early_stopping
python3 autostop.py
```

### **[IMPORTANT] Ensure that iperf server is running on the destination machine before proceeding!**

The program will ask you for the command to run. By default, it will run `iperf -c 127.0.0.1 -t 60 -i 0.25`

Next, it will ask you to specify the breakpoint in Gbits/sec with a default of 80 Gb/s.

The program will then run the command until the output contains the specified breakpoint.

**NOTE:** This program is designed to measure throughput over 1 Gbit/sec. Modifications are necessary to measure slower throughput speeds.
