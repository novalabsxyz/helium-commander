#!/usr/bin/env python

import helium.service as helium

def sensor_timeseries(service, sensor_id, writer, **kwargs):
    json_data = lambda json: json['data'] if json else None

    # Get the first page
    res = service.get_sensor_timeseries(sensor_id, **kwargs)
    writer(json_data(res))
    while res != None:
        res = service.get_prev_page(res)
        writer(json_data(res))

def reading_port_filter(ports):
    if ports == None:
        def port_filter(reading): return True
    else:
        def port_filter(reading):
            return reading['meta']['port'] in ports
    return port_filter

def json_writer(file, port_filter):
    first_reading = [True] # Storing in an array to avoid non local errors in 2.7
    file.write('[')
    def writer(readings):
        if readings is None:
            file.write(']')
        else:
            for reading in filter(port_filter, readings):
                if first_reading[0]:
                    first_reading[0] = False
                else:
                    file.write(',')
                    file.write(json.dumps(reading))
    return writer

def csv_writer(file, port_filter):
    fieldnames = ['sensor-id', 'reading-id', 'timestamp-utc', 'port', 'value']
    csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
    csv_writer.writeheader()
    def writer(readings):
        if readings is None: return None
        for reading in filter(port_filter, readings):
            row = { 'reading-id': reading['id'],
                    'sensor-id': reading['relationships']['sensor']['data']['id'],
                    'timestamp-utc': reading['meta']['timestamp'],
                    'port': reading['meta']['port'],
                    'value': reading['meta']['value']
            }
            csv_writer.writerow(row)
    return writer

if __name__ == "__main__":
    import sys, argparse, csv, json

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', default='csv', choices=['csv', 'json'],
                        help='The output format for the results (default \'csv\')')
    parser.add_argument('-s', '--page-size', type=int, default=5000,
                        help='The page size for each page')
    parser.add_argument('-p', '--port', nargs='+',
                        help='The ports to filter readings on')
    parser.add_argument('-o', '--output', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='The output to write to (default stdout)')
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')
    parser.add_argument('sensor_id',
                        help='The sensor id to get timeseries data for')
    opts = parser.parse_args()
    service = helium.Service(opts.api_key)

    with opts.output as file:
        port_filter = reading_port_filter(opts.port)
        if opts.format == 'json':
            write_readings = json_writer(file, port_filter)
        elif opts.format == 'csv':
            write_readings = csv_writer(file, port_filter)

        sensor_timeseries(service, opts.sensor_id,
                          write_readings,
                          page_size = opts.page_size)
