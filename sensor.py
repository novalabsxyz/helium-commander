#!/usr/bin/env python

import pytz
import datetime
import dateutil.parser
import requests

BASE_URL = "https://api.helium.com/v1/"

session = requests.Session()

def sensor(api_key,  writer):
    url = BASE_URL + 'sensor'
    headers = {'Authorization': api_key}
    json_data = lambda json: json['data']

    req = session.get(url, headers=headers)
    res = req.json()
    writer(json_data(res))

if __name__ == "__main__":
    import sys, argparse, csv, json

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='The output to write to (default stdout)')
    parser.add_argument('-f', '--format', default='csv', choices=['csv', 'json'],
                        help='The output format for the results (default \'csv\')')
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')
    opts = parser.parse_args()

    with opts.output as file:

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
