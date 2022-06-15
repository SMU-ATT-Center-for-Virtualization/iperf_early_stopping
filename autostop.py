import shlex
import subprocess
import sys
import scipy.stats as st
import numpy
import os
import signal
import argparse
import re

def live_read(command : str, interval : float, width : float, minSamples : int, numToSkip : int) -> bool:
    output_array = []
    width_achieved = False
    current_samples = 0
    try:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE)
        values = []
    except:
        print("Error: command not found")
        sys.exit(1)
    for output in process.stdout:
        print('here')
        if output == '':
            continue
        print(f'current samples {current_samples}')
        output = output.strip().decode('utf-8')
        print(output)
        output_array.append(output)

        if not width_achieved:

            throughput_match = re.search(r'(?P<throughput>\d+\.?\d+?)\s+\wbits\/sec', 
                                     output)
            if throughput_match:
                throughput = float(throughput_match.group('throughput'))
                current_samples += 1
                if current_samples <= numToSkip:
                    continue

                print("using this value")
                values.append(throughput)

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
    with open('iperf_output.txt', 'w') as f:
        for line in output_array:
            f.write(line)
            f.write('\n')

    return width_achieved


def main(argv):
    # Parse command line arguments
    command = "iperf -c 127.0.0.1 -t 60 -i 0.25 -f m"
    level = 0.95
    width = 2.5
    minSamples = 10
    numToSkip = 10

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', help='iPerf2 command to execute')
    parser.add_argument('-l', '--confidence_level', help='Desired confidence level', type=float)
    parser.add_argument('-w', '--interval_percentage_width', 
                        help='The percentage width of the confidence interval, +-. Ex. If you give'
                             ' a value of 2.5, this will try for an interval with a +-2.5 percent width',
                        type=float)
    parser.add_argument('-m', '--min_samples', help='The minimum number of samples to use', type=int)
    parser.add_argument('-s', '--skip', help='this will skip n samples at the beginning of the test',
                        type=int)


    args = parser.parse_args()

    print(args)

    if args.command:
        command = args.command
    if args.confidence_level:
        level = args.confidence_level
    if args.interval_percentage_width:
        width = args.interval_percentage_width
    if args.min_samples:
        minSamples = args.min_samples
    if args.skip:
        numToSkip = args.skip

    success = live_read(command, level, width, minSamples, numToSkip)
    if not success:
        print("Did not attain target")


if __name__ == "__main__":
    main(sys.argv[1:])
