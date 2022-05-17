import shlex
import subprocess
import sys
import scipy.stats as st
import numpy

def live_read(command, interval, width, minSamples, numToSkip):
    try:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE)
        values = []
    except:
        print("Error: command not found")
        sys.exit(1)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            output = output.strip().decode('utf-8')
            outputList = output.split(" ")
            # print(outputList)
            # 
            
            for i in range(0, len(outputList)):
                try:
                    if outputList[i] == 'Gbits/sec':
                        values.append(float(outputList[i-1]))
                        print(float(outputList[i-1]))
                except ValueError:
                    continue
                
            print(values)
            deg_freedom = len(values) - 1
            sample_mean = numpy.nanmean(values)
            sample_stderr = st.sem(values)
            ci = st.t.interval(interval, deg_freedom, sample_mean, sample_stderr)
            print(ci)
            int_width = abs(sample_mean-ci[0])
            print("Width: " + str(int_width))
            # for v in values:
                # if v >= float(breakpoint):
                #     print("Bitrate exceeded threshold")
                #     sys.exit(1)
                    # Change to when width reaches within a certain percentage from the mean (X bar minus right side of plus minus)
    rc = process.poll()
    return rc


def main():
    command = input("Enter command to execute [Default iperf -c 127.0.0.1 -t 60 -i 0.25]:")
    if command == "":
        command = "iperf -c 127.0.0.1 -t 60 -i 0.25"
    while True:
        breakpoint = input("Enter bitrate threshold in Gbits/sec [Default 80]:")
        if breakpoint == "":
            breakpoint = 80
        try:
            float(breakpoint)
            break
        except ValueError:
            print("Invalid input, please try again")
    # Things to ask user input: 
    # Confidence interval percentage (95%, 90%, etc)
    while True:
        interval = input("Enter the confidence interval as a decimal [Default 0.95]:")
        if interval == "":
            interval = 0.95
        try:
            float(interval)
            break
        except ValueError:
            print("Invalid input, please try again")
    # Desired width and minimum # of samples
    while True:
        width = input("Enter target interval width [Default 2]:")
        if width == "":
            width = 2
        try:
            float(width)
            break
        except ValueError:
            print("Invalid input, please try again")
    while True:
        minSamples = input("Enter minimum number of samples [Default 10]:")
        if minSamples == "":
            minSamples = 10
        try:
            float(minSamples)
            break
        except ValueError:
            print("Invalid input, please try again")
    # Skip a few initial samples specified by user, default would be like 10, can be samples or seconds
    while True:
        numToSkip = input("Enter number of samples to skip [Default 10]:")
        if numToSkip == "":
            numToSkip = 10
        try:
            float(breakpoint)
            break
        except ValueError:
            print("Invalid input, please try again")

    while True:
        live_read(command, interval, width, minSamples, numToSkip)

main()
