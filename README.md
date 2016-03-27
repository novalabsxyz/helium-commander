# Helium API Examples

## Setup

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

## Usage

``` shellsession
 ./helium-commander.py --help
usage: helium-commander.py [-h] -k API_KEY
                           [--format {csv,tsv,json,yaml,html,xls,xlsx,latex}]
                           {label,sensor,element,timeseries} ...

positional arguments:
  {label,sensor,element,timeseries}
                        one of the helium commands

optional arguments:
  -h, --help            show this help message and exit
  -k API_KEY, --api-key API_KEY
                        your Helium API key. Can also be specified using the
                        HELIUM_API_KEY environment variable
  --format {csv,tsv,json,yaml,html,xls,xlsx,latex}
                        the output format for the results
```

*Note* that each of the top level commands has their own set of sub-commands
with their own features and flags. Run each of them with -h to find out more.

For example:

``` shellsession

 ./helium-commander.py timeseries -h
usage: helium-commander.py timeseries [-h] {dump,list} ...

positional arguments:
  {dump,list}
    dump       dump timeseries data to files. Note that --dump-format
               determines the file format
    list       list timeseries data for a given sensor

optional arguments:
  -h, --help   show this help message and exit


```
