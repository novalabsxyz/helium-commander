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


def sensor(api_key,  writer):
    url = BASE_URL + 'sensor'
    headers = {'Authorization': api_key}
    json_data = lambda json: json['data']

    # get the first page, which has no `before` parameter
    _print("Getting data from Helium ")
    req = session.get(url, headers=headers)
    _print('.')
    res = req.json()
    writer(json_data(res))

if __name__ == "__main__":
    import sys, argparse, csv, json

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')
    parser.add_argument('-f', '--format', default='csv', choices=['csv', 'json'],
                        help='The output format for the results (default \'csv\')')
    opts = parser.parse_args()

    output_file = 'sensor' + '.'+ opts.format
    print("Writing to " +  output_file)


    with open(output_file, 'w') as file:

        if opts.format == 'json':
            def write_values(values):
                file.write(json.dumps(values))

        elif opts.format == 'csv':
            fieldnames = ['sensor-id', 'sensor-name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            def write_values(values):
                for value in values:
                    row = { 'sensor-name': value['attributes']['name'],
                            'sensor-id': value['id']
                    }
                    writer.writerow(row)

        sensor(opts.api_key, write_values)
