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
usage: sensor-timeseries.py [-h] [--format {csv,json}] [--page-size PAGE_SIZE]
                            [--port PORT [PORT ...]] -k API_KEY
                            [-s SENSOR [SENSOR ...] | -l LABEL | -o]

optional arguments:
  -h, --help            show this help message and exit
  --format {csv,json}   The output format for the results (default 'csv')
  --page-size PAGE_SIZE
                        The page size for each page
  --port PORT [PORT ...]
                        The ports to filter readings on
  -k API_KEY, --api-key API_KEY
                        Your Helium API key
  -s SENSOR [SENSOR ...], --sensor SENSOR [SENSOR ...]
                        Get timeseries data for one or more sensors
  -l LABEL, --label LABEL
                        Get timeseries data for all sensors in a label
  -o, --org             Get timeseries data for all sensors in the
                        organization
```

``` shellsession
./sensor.py -h
usage: sensor.py [-h] [--format {csv,json}] [-o [OUTPUT]] -k API_KEY

optional arguments:
  -h, --help            show this help message and exit
  --format {csv,json}   The output format for the results (default 'csv')
  -o [OUTPUT], --output [OUTPUT]
                        The output to write to (default stdout)
  -k API_KEY, --api-key API_KEY
                        Your Helium API key
```
