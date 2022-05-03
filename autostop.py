import shlex
import subprocess
import sys

def live_read(command, breakpoint):
    try:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE)
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
            values = []
            for i in range(0, len(outputList)):
                try:
                    if outputList[i] == 'Gbits/sec':
                        values.append(float(outputList[i-1]))
                        print(float(outputList[i-1]))
                except ValueError:
                    continue
                
            print(output)
            for v in values:
                if v >= float(breakpoint):
                    print("Bitrate exceeded threshold")
                    sys.exit(1)
    rc = process.poll()
    return rc


def main(argv):
    command = input("Enter command to execute [Default iperf -c 127.0.0.1 -t 60 -i 0.25]:")
    if command == "":
        command = "iperf -c 127.0.0.1 -t 60 -i 0.25"
    breakpoint = input("Enter bitrate threshold in Gbits/sec [Default 80]:")
    if breakpoint == "":
        breakpoint = 80
    try:
        float(breakpoint)
    except ValueError:
        print("Invalid input")
        sys.exit(1)
    
    while True:
        live_read(command, breakpoint)

main(sys.argv)
