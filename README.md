# Helium API Examples

## Setup

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

## Usage

Run each script with `-h` to get help on running the script and what
parameters it supports

For example:


``` shellsession
./sensor-timeseries.py -h
usage: sensor-timeseries.py [-h] [-f {csv,json}] [-s PAGE_SIZE]
                            [-p PORT [PORT ...]] [-o [OUTPUT]] -k API_KEY
                            sensor_id

positional arguments:
  sensor_id             The sensor id to get timeseries data for

optional arguments:
  -h, --help            show this help message and exit
  -f {csv,json}, --format {csv,json}
                        The output format for the results (default 'csv')
  -s PAGE_SIZE, --page-size PAGE_SIZE
                        The page size for each page
  -p PORT [PORT ...], --port PORT [PORT ...]
                        The ports to filter readings on
  -o [OUTPUT], --output [OUTPUT]
                        The output to write to (default stdout)
  -k API_KEY, --api-key API_KEY
                        Your Helium API key
```
