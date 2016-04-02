from concurrent import futures
import _dump_writer as writer
import dpath.util as dpath
import io
import helium

def _filter_timeseries(data, ports=None):
    if data is None or ports is None: return data
    return [ item for item in data if item['meta']['port'] in ports ]

def _dump_get_sensors(service, opts):
    if opts.sensors is not None:
        return opts.sensors
    elif opts.label is not None:
        labels = service.get_label(opts.label)
        return dpath.values(labels, 'data/relationships/sensor/data/*/id')
    elif opts.org:
        sensors = service.get_sensors()
        return dpath.values(sensors, '/data/*/id')

def _process_sensor_timeseries(service, sensor_id, writer, ports = None, **kwargs):
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

def _dump_timeseries(sensor_id, opts):
    with io.BufferedWriter(io.FileIO(sensor_id + '.' + opts.dump_format, "wb")) as file:
        csv_mapping = {
            'reading-id': 'id',
            'sensor-id': 'relationships/sensor/data/id',
            'timestamp-utc': 'meta/timestamp',
            'port': 'meta/port',
            'value': 'meta/value'
        }
        output = writer.writer_for_opts(opts, file, mapping=csv_mapping)
        service = helium.Service(opts.api_key)
        return _process_sensor_timeseries(service, sensor_id, output, opts.port, page_size=opts.page_size)


def dump(service ,opts):
    sensors = _dump_get_sensors(service, opts)
    with futures.ProcessPoolExecutor(max_workers=10) as executor:
        sensor_futures = dict((executor.submit(_dump_timeseries, sensor_id, opts),
                               sensor_id) for sensor_id in sensors)
        futures.wait(sensor_futures)

def list(service, opts):
    if opts.sensor:
        data = service.get_sensor_timeseries(opts.sensor, page_size=opts.page_size).get("data")
    else:
        data = service.get_org_timeseries(page_size=opts.page_size).get("data")

    return _filter_timeseries(data, opts.port)


def _register_commands(parser):
    dump_parser = parser.add_parser("dump",
                                    help="dump timeseries data for a label, sensors or the whole organization to files. Note that --dump-format determines the file format")
    ## Dump
    dump_parser.set_defaults(command=dump)
    dump_parser.add_argument('--page-size', type=int, default=5000,
                             help='the page size for each page')
    dump_parser.add_argument('--port', nargs='+',
                             help='the ports to filter readings on')
    writer.add_writer_arguments(dump_parser)
    # Mutually exclusive sources to get timeseries data for
    dump_source_group = dump_parser.add_mutually_exclusive_group(required=True)
    dump_source_group.add_argument('-s', '--sensors', metavar="SENSOR", nargs='+',
                                   help='the id for a sensor')
    dump_source_group.add_argument('-l', '--label',
                                   help='the id for a label')
    dump_source_group.add_argument('-o', '--org', action="store_true",
                                   help='timeseries data for all sensors in the organization')

    ## List
    list_mapping = [
        ('id', 'id'),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port'),
        ('value', 'attributes/value')
    ]
    list_parser = parser.add_parser("list",
                                    help="list timeseries data for a given sensor or the organization timeseries")
    list_parser.set_defaults(command=list, mapping=list_mapping)
    list_parser.add_argument('--page-size', type=int, default=20,
                             help='the number of readings to get')
    list_parser.add_argument('--port', nargs='+',
                             help='the ports to filter readings on')
    list_source_group = list_parser.add_mutually_exclusive_group(required=True)
    list_source_group.add_argument("-s", '--sensor', metavar="SENSOR",
                                   help="the id of the sensor to fetch readings for")
    list_source_group.add_argument("-o", '--org', action="store_true",
                                   help="fetch timeseries data for the organization endpoint")
