import sys

import numpy

def main():
    if len(sys.argv) < 2:
        return

    data = []

    for filename in sys.argv[2:]:
        with open(filename, "r") as file:
            for line in file:
                data.append(line.strip())

    words = []
    latency = []
    total_time = []

    for line in data:
        if line.startswith("[llm] "):
            line = line.removeprefix("[llm] ")
            line = line.split()
            words.append(len(line))
        elif line.startswith("[timer]"):
            line = line.removeprefix("[timer] ")
            line = line.split()
            latency.append(int(line[1].removesuffix("ms,")))
            total_time.append(int(line[3].removesuffix("ms")))

    wps = []

    for i in range(len(words)):
        time = total_time[i] - latency[i]
        wps.append(words[i] / (time / 1000))

    wps = numpy.array(wps)
    wps_average = numpy.average(wps)
    wps_q1 = numpy.percentile(wps, 25)
    wps_q3 = numpy.percentile(wps, 75)

    print(f"Average WPS: {wps_average}")
    print(f"25th Percentile (Q1): {wps_q1}")
    print(f"75th Percentile (Q3): {wps_q3}")
    print()

    latency = numpy.array(latency)
    latency_average = numpy.average(latency)
    latency_q1 = numpy.percentile(latency, 25)
    latency_q3 = numpy.percentile(latency, 75)

    print(f"Average Latency: {latency_average} ms")
    print(f"25th Percentile (Q1): {latency_q1} ms")
    print(f"75th Percentile (Q3): {latency_q3} ms")
    print()

    total_time = numpy.array(total_time)
    total_time_average = numpy.average(total_time)
    total_time_q1 = numpy.percentile(total_time, 25)
    total_time_q3 = numpy.percentile(total_time, 75)

    print(f"Average Total Time: {total_time_average} ms")
    print(f"25th Percentile (Q1): {total_time_q1} ms")
    print(f"75th Percentile (Q3): {total_time_q3} ms")

if __name__ == "__main__":
    main()
