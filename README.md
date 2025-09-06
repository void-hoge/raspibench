# raspibench

usage: raspibench.py [-h] -c COMMAND [-i INTERVAL] [-o OUTPUT] [--pre PRE]
                     [--post POST]

Raspberry Pi benchmark

options:
  -h, --help            show this help message and exit
  -c COMMAND, --command COMMAND
                        Load command to run
  -i INTERVAL, --interval INTERVAL
                        Sampling interval in seconds (default: 1)
  -o OUTPUT, --output OUTPUT
                        CSV output file path.
  --pre PRE             Seconds to sample at idle before starting the load
                        command (default: 30.0)
  --post POST           Seconds to sample at idle after starting the load
                        command (default: 30.0)
