#!/usr/bin/env python

import helium.service as helium
import dpath.util as dpath

def sensor_timeseries(service, sensor_id, writer, ports = None, **kwargs):
    def json_data(json, ports):
        data = json['data'] if json else None
        if data is None or ports is None: return data
        return [ item for item in data if item['meta']['port'] in ports ]

    # Get the first page
    res = service.get_sensor_timeseries(sensor_id, **kwargs)
    writer.start()
    writer.write_readings(json_data(res, ports))
    while res != None:
        res = service.get_prev_page(res)
        writer.write_readings(json_data(res, ports))
    writer.finish()

def get_sensors(service, opts):
    if opts.sensor is not None:
        return opts.sensor
    elif opts.label is not None:
        labels = service.get_label(opts.label)
        return dpath.values(labels, 'data/relationships/sensor/data/*/id')
    elif opts.org:
        sensors = service.get_sensors()
        return dpath.values(sensors, '/data/*/id')

def reading_port_filter(ports):
    if ports == None:
        def port_filter(reading): return True
    else:
        def port_filter(reading):
            return reading['meta']['port'] in ports
    return port_filter

if __name__ == "__main__":
    import argparse, io
    from concurrent import futures
    import util.writer as writer

    parser = argparse.ArgumentParser()

    writer.add_writer_arguments(parser)
    parser.add_argument('--page-size', type=int, default=5000,
                        help='The page size for each page')
    parser.add_argument('--port', nargs='+',
                        help='The ports to filter readings on')
    parser.add_argument('-k', '--api-key',  required=True,
                        help='Your Helium API key')

    # Mutually exclusive sources to get timeseries data for
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument('-s', '--sensor', nargs='+',
                              help='Get timeseries data for one or more sensors')
    source_group.add_argument('-l', '--label',
                              help='Get timeseries data for all sensors in a label')
    source_group.add_argument('-o', '--org', action='store_true',
                              help='Get timeseries data for all sensors in the organization')

    opts = parser.parse_args()
    service = helium.Service(opts.api_key)
    sensors = get_sensors(service, opts)

    def timeseries(sensor_id, opts):
        with io.BufferedWriter(io.FileIO(sensor_id + '.' + opts.format, "wb")) as file:
            csv_mapping = {
                'reading-id': 'id',
                'sensor-id': 'relationships/sensor/data/id',
                'timestamp-utc': 'meta/timestamp',
                'port': 'meta/port',
                'value': 'meta/value'
            }
            output = writer.writer_for_opts(opts, file, mapping=csv_mapping)
            service = helium.Service(opts.api_key)
            return sensor_timeseries(service, sensor_id, output, opts.port, page_size=opts.page_size)

    sensor_timeseries(service, sensors[0], output, opts.port, page_size=opts.page_size)
    with futures.ProcessPoolExecutor(max_workers=10) as executor:
        sensor_futures = dict((executor.submit(timeseries, sensor_id, opts),
                               sensor_id) for sensor_id in sensors)
        futures.wait(sensor_futures)
