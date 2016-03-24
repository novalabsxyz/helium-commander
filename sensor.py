#!/usr/bin/env python

import helium.service as helium
import util.writer as writer

def sensor(service,  writer):
    json_data = lambda json: json['data']
    res = service.get_sensors()
    writer.start()
    writer.write_readings(json_data(res))
    writer.finish()

if __name__ == "__main__":
    import sys, argparse, io

    parser = argparse.ArgumentParser()
    writer.add_writer_arguments(parser)
    parser.add_argument('-o', '--output', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='The output to write to (default stdout)')
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')

    opts = parser.parse_args()
    service = helium.Service(opts.api_key)

    with opts.output as file:
        csv_mapping = {
            'sensor-name': 'attributes/name',
            'sensor-id': 'id'
        }
        output = writer.writer_for_opts(opts, file, mapping = csv_mapping)
        sensor(service, output)
