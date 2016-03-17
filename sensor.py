#!/usr/bin/env python

import helium.service as helium

def sensor(service,  writer):
    json_data = lambda json: json['data']
    res = service.get_sensors()
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

    service = helium.Service(opts.api_key)

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

        sensor(service, write_values)
