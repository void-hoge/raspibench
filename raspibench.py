#!/usr/bin/env python3

import argparse
import shlex
import subprocess
import sys
import threading
import time

CPUFREQ_CMD = ['vcgencmd', 'measure_clock', 'arm']
THERMAL_PATH = '/sys/class/thermal/thermal_zone0/temp'
COOLER_PATH = '/sys/class/thermal/cooling_device0/cur_state'


def sample_once():
    _, freq = subprocess.run(CPUFREQ_CMD, capture_output=True, text=True).stdout.split('=')
    temp = open(THERMAL_PATH).read()
    try:
        cooler = open(COOLER_PATH).read()
    except:
        cooler = '0'
    return int(freq), int(temp), bool(int(cooler))


def sampler(stop_event, started_event, interval, path):
    with open(path, 'w') as f:
        print('phase, frequency, tempareture, cooler', file=f)
        current = time.time()
        while not stop_event.is_set():
            phase = True if started_event.is_set() else False
            freq, temp, cooler = sample_once()
            print(f'{int(phase)}, {freq}, {temp}, {int(cooler)}', file=sys.stderr)
            print(f'{int(phase)}, {freq}, {temp}, {int(cooler)}', file=f)
            current += interval
            remain = current - time.time()
            if remain > 0:
                stop_event.wait(timeout=remain)


def stresser(stop_event, started_event, pre, post, command):
    print(f'[INFO] Idle for {pre:.1f}s...', file=sys.stderr)
    stop_event.wait(timeout=pre)
    started_event.set()
    subprocess.run(shlex.split(command))
    started_event.clear()
    print(f'[INFO] Idle for {post:.1f}s...', file=sys.stderr)
    stop_event.wait(timeout=post)
    stop_event.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Raspberry Pi benchmark')
    parser.add_argument('-c', '--command', required=True, help='Load command to run')
    parser.add_argument('-i', '--interval', type=float, default=1.0, help='Sampling interval in seconds (default: 1)')
    parser.add_argument('-o', '--output', default='bench.csv', help='CSV output file path.')
    parser.add_argument(
        '--pre',
        type=float,
        default=10.0,
        help='Seconds to sample before starting the load command (default: 30.0)',
    )
    parser.add_argument(
        '--post',
        type=float,
        default=60.0,
        help='Seconds to sample after completing the load command (default: 30.0)',
    )
    args = parser.parse_args()

    stop_event = threading.Event()
    started_event = threading.Event()

    sampler_thread = threading.Thread(target=sampler, args=(stop_event, started_event, args.interval, args.output))
    stresser_thread = threading.Thread(
        target=stresser, args=(stop_event, started_event, args.pre, args.post, args.command)
    )

    sampler_thread.start()
    stresser_thread.start()
    sampler_thread.join()
    stresser_thread.join()
