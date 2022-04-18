# iperf_early_stopping

## Introduction

This Python script allows you to run iperf3 until a specified bandwidth is reached.

## How to run

First, clone the repository:

```bash
git clone
```

Then, run the following command:

```bash
cd iperf_early_stopping
python3 autostop.py
```

The program will ask you for the command to run. By default, it will run `iperf3 -c 127.0.0.1 -t 1 -i 0.25`

Next, it will ask you to specify the breakpoint in Gbits/sec with a default of 50 Gb/s.

The program will then run the command until the output contains the specified breakpoint.