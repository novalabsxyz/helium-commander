#!/usr/bin/env python

import pytz
import datetime
import dateutil.parser
import requests
import sys

BASE_URL = "https://api.helium.com/v1/"

session = requests.Session()

def _print(str):
    sys.stdout.write(str)
    sys.stdout.flush()

def get_json_path(json, path):
    try: # try to get the value
        return reduce(dict.__getitem__, path, json)
    except KeyError:
        return None


def sensor_timeseries(api_key, sensor_id, page_size, writer):
    url = BASE_URL + 'sensor/' + sensor_id + '/timeseries?page[size]=' + str(page_size)
    headers = {'Authorization': api_key}
    json_prev_url = lambda json: get_json_path(json, ["links", "prev"])
    json_data = lambda json: json['data']

    # get the first page, which has no `before` parameter
    _print("Getting data from Helium ")
    req = session.get(url, headers=headers)
    _print('.')
    res = req.json()

    writer(json_data(res), False)
    prev_url = json_prev_url(res)
    while prev_url != None:
        res = []
        sys.stdout.write('.')
        req = session.get(prev_url, headers=headers)
        _print('.')
        res = req.json()
        prev_url = json_prev_url(res)
        writer(json_data(res), False)
    _print('\n')
    writer([], True)

if __name__ == "__main__":
    import sys, argparse, csv, json

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')
    parser.add_argument('-f', '--format', default='csv', choices=['csv', 'json'],
                        help='The output format for the results (default \'csv\')')
    parser.add_argument('-s', '--page-size', type=int, default=1000,
                        help='The page size for each page')
    parser.add_argument('sensor_id',
                        help='The sensor id to get timeseries data for')
    opts = parser.parse_args()

    output_file = opts.sensor_id + '.' + opts.format
    print("Writing to " +  output_file)

    with open(output_file, 'w') as file:

        if opts.format == 'json':
            first_reading = [True] # Storing in an array to avoid non local errors in 2.7
            file.write('[')
            def write_readings(readings, done):
                for reading in readings:
                    if first_reading[0]:
                        first_reading[0] = False
                    else:
                        file.write(',')
                    file.write(json.dumps(reading))
                if done: file.write(']')


        elif opts.format == 'csv':
            fieldnames = ['sensor-id', 'reading-id', 'timestamp-utc', 'port', 'value']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            def write_readings(readings, done):
                for reading in readings:
                    row = { 'reading-id': reading['id'],
                            'sensor-id': reading['relationships']['sensor']['data']['id'],
                            'timestamp-utc': reading['meta']['timestamp'],
                            'port': reading['meta']['port'],
                            'value': reading['meta']['value']
                    }
                    writer.writerow(row)

        sensor_timeseries(opts.api_key, opts.sensor_id, opts.page_size, write_readings)
