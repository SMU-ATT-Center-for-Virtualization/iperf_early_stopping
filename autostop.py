import shlex
import subprocess
import sys
import scipy.stats as st
import numpy
import os
import signal

def live_read(command : str, interval : float, width : float, minSamples : int, numToSkip : int):
    output_array = []
    width_achieved = False
    try:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE)
        values = []
        current_samples = 0
    except:
        print("Error: command not found")
        sys.exit(1)
    for output in process.stdout:
        output = output.strip().decode('utf-8')
        print(output)
        output_array.append(output)
        outputList = output.split(" ")

        if not width_achieved:
            for i in range(0, len(outputList)):
                try:
                    if outputList[i] == 'Gbits/sec':
                        if current_samples < numToSkip:
                            continue
                        else:
                            values.append(float(outputList[i-1]))
                            print(float(outputList[i-1]))
                    current_samples += 1
                except ValueError:
                    continue
            if len(values) >= minSamples:
                print(values)
                deg_freedom = len(values) - 1
                sample_mean = numpy.nanmean(values)
                sample_sem = st.sem(values)
                ci = st.t.interval(interval, deg_freedom, sample_mean, sample_sem)
                print(ci)
                int_width = abs(sample_mean-ci[0])
                print("Width: " + str(int_width))
                if int_width < width:
                    width_achieved = True
                    print("Target reached!")
                    print("Final mean: " + str(sample_mean))
                    print("Final confidence interval: " + str(ci))
                    print("Final width: " + str(int_width))
                    process.send_signal(signal.SIGINT)

    # TODO, write this output to a file for parsing later
    print(output_array)
    return width_achieved


def main():
    command = input("Enter command to execute [Default iperf -c 127.0.0.1 -t 60 -i 0.25]:")
    if command == "":
        command = "iperf -c 127.0.0.1 -t 60 -i 0.25"
    # Things to ask user input: 
    # Confidence interval percentage (95%, 90%, etc)
    while True:
        interval = input("Enter the desired confidence level as a decimal [Default 0.95]:")
        if interval == "":
            interval = 0.95
        try:
            interval = float(interval)
            break
        except ValueError:
            print("Invalid input, please try again")
    # Desired width and minimum # of samples
    while True:
        width = input("Enter target interval percentage width (+/-) [Default 2.5]:")
        if width == "":
            width = 2.5
        try:
            width = float(width)
            break
        except ValueError:
            print("Invalid input, please try again")
    while True:
        minSamples = input("Enter minimum number of samples [Default 20]:")
        if minSamples == "":
            minSamples = int(10)
        try:
            minSamples = int(minSamples)
            break
        except ValueError:
            print("Invalid input, please try again")
    # Skip a few initial samples specified by user, default would be like 10, can be samples or seconds
    while True:
        numToSkip = input("Enter number of samples to skip [Default 10]:")
        if numToSkip == "":
            numToSkip = int(10)
        try:
            numToSkip = int(numToSkip)
            break
        except ValueError:
            print("Invalid input, please try again")

    success = live_read(command, interval, width, minSamples, numToSkip)
    if not success:
        print("Did not attain target")

main()
