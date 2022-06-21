import shlex
import subprocess
import sys
import scipy.stats as st
import numpy
import os
import signal
import argparse
import re

def live_read(command : str, interval : float, width : float, minSamples : int, numToSkip : int,
              output_file: str = None) -> bool:
    print(f'TARGET WIDTH: {width}')
    output_array = []
    width_achieved = False
    current_samples = 0
    cmdcpy = str(command)
    multithread = False
    try:
        multithread = re.search(r'-P (?P<threadCount>\d*)', cmdcpy)
        if int(multithread.group('threadCount')) > 1:
            multithread = True
        else:
            multithread = False
    except AttributeError:
        multithread = False
    
    try:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE)
        values = []
    except:
        print("Error: command not found")
        sys.exit(1)
    for output in process.stdout:
        if output == '':
            continue
        # print(f'current samples {current_samples}')
        output = output.strip().decode('utf-8')
        print(output)
        output_array.append(output)

        if not width_achieved and not multithread or re.search('\[SUM\]', output):
            print('Using '+ output)
            throughput_match = re.search(r'(?P<throughput>\d+\.?\d+?)\s+\wbits\/sec', 
                                     output)
            if throughput_match:
                throughput = float(throughput_match.group('throughput'))
                current_samples += 1
                if current_samples <= numToSkip:
                    continue

                # print("using this value")
                values.append(throughput)

                if len(values) >= minSamples:
                    # print(values)
                    deg_freedom = len(values) - 1
                    sample_mean = numpy.nanmean(values)
                    sample_sem = st.sem(values)
                    ci = st.t.interval(interval, deg_freedom, sample_mean, sample_sem)
                    # print(ci)
                    interval_width = abs(sample_mean-ci[0])
                    interval_percent_width = (interval_width/sample_mean)*100
                    print("Width: " + str(interval_percent_width))
                    if interval_percent_width < width:
                        width_achieved = True
                        print("Target reached!")
                        print(f"Final mean: {sample_mean}")
                        print(f"Final confidence interval: {ci}")
                        print(f"Final width: +-{interval_percent_width}%")
                        print(f"Number of Samples: {len(values)}" )
                        process.send_signal(signal.SIGINT)

    # Write this output to a file for parsing later
    # print(output_array)
    if not width_achieved:
        deg_freedom = len(values) - 1
        sample_mean = numpy.nanmean(values)
        sample_sem = st.sem(values)
        ci = st.t.interval(interval, deg_freedom, sample_mean, sample_sem)
        # print(ci)
        interval_width = abs(sample_mean-ci[0])
        interval_percent_width = (interval_width/sample_mean)*100
        print("Target not reached!")
        print(f"Final mean: {sample_mean}")
        print(f"Final confidence interval: {ci}")
        print(f"Final width: +-{interval_percent_width}%")
        # subtract 1 because this will count the end summary otherwise
        print(f"Number of Samples: {len(values) - 1}" )
    if output_file:
        with open(output_file, 'w') as f:
            for line in output_array:
                f.write(line)
                f.write('\n')

    return width_achieved


def main(argv):
    # Parse command line arguments
    command = "iperf -c 127.0.0.1 -t 60 -i 0.25 -f m -P 2"
    level = 0.95
    width = 2.5
    minSamples = 10
    numToSkip = 10
    output_file = None

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
    parser.add_argument('-o', '--output_file', help='File to write iperf results to')


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
    if args.output_file:
        output_file = args.output_file

    success = live_read(command, level, width, minSamples, numToSkip, output_file)
    if not success:
        print("Did not attain target")


if __name__ == "__main__":
    main(sys.argv[1:])
