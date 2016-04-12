from concurrent import futures
import dpath.util as dpath
import helium
import click
import util
import csv
import json
import abc


def format_option():
    options = [
        click.option('--format', type=click.Choice(['csv', 'json']), default='csv',
                     help="the format of the readings")
    ]
    def wrapper(func):
        for option in options:
            func = option(func)
        return func
    return wrapper

def options(page_size=20):
    options = [
        click.option('--page-size', default=page_size,
                     help="the number of readings to get per request"),
        click.option('--port', multiple=True,
                     help="the port to filter readings on"),
        click.option('--start',
                     help="the start date to filter readings on"),
        click.option('--end',
                     help="the end date to filter readings on"),
    ]

    def wrapper(func):
        for option in options:
            func = option(func)
        return func
    return wrapper


def tabulate(result):
    if not result:
        click.echo('No data')
        return
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port'),
        ('value', 'attributes/value')
    ]))


def dump(service, sensors, format, **kwargs):
    with click.progressbar(length=len(sensors), label="Dumping", show_eta=False, width=50) as bar:
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            all_futures = []
            for sensor_id in sensors:
                future = executor.submit(_dump_one, service, sensor_id, format, **kwargs)
                future.add_done_callback(lambda f: bar.update(1))
                all_futures.append(future)
            result_futures = futures.wait(all_futures, return_when=futures.FIRST_EXCEPTION)
            for future in result_futures.done:
                future.result() # re-raises the exception

def _dump_one(service, sensor_id, format, **kwargs):
    filename = (sensor_id+'.'+format).encode('ascii', 'replace')
    with click.open_file(filename, "wb") as file:
        csv_mapping = {
            'id': 'id',
            'sensor': 'relationships/sensor/data/id',
            'timestamp': 'attributes/timestamp',
            'port': 'attributes/port',
            'value': 'attributes/value'
        }
        service = helium.Service(service.api_key, service.base_url)
        writer = _writer_for_format(format, file, mapping=csv_mapping)
        writer.process_timeseries(service, sensor_id, **kwargs)


#
# Writer classes
#

def _writer_for_format(format, file, **kwargs):
    if format == 'json':
        return _JSONWriter(file, **kwargs)
    elif format == 'csv':
        return _CSVWriter(file, **kwargs)

class _BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file

    def process_timeseries(self, service, sensor_id, **kwargs):
        def json_data(json):
            return json['data'] if json else None
        # Get the first page
        res = service.get_sensor_timeseries(sensor_id, **kwargs)
        self.start()
        self.write_readings(json_data(res))
        while res != None:
            res = service.get_prev_page(res)
            self.write_readings(json_data(res))
        self.finish()

    def start(self):
        return

    @abc.abstractmethod
    def write_readings(self, readings):
        return

    def finish(self):
        return

class _CSVWriter(_BaseWriter):
    def __init__(self, file, **kwargs):
        super(_CSVWriter, self).__init__(file, **kwargs)
        self.mapping = kwargs['mapping']
        self.writer = csv.DictWriter(file, self.mapping.keys())

    def start(self):
        self.writer.writeheader()

    def write_readings(self, readings):
        if readings is None: return
        for reading in readings:
            row = { key: dpath.get(reading, path) for key, path in self.mapping.iteritems() }
            self.writer.writerow(row)


class _JSONWriter(_BaseWriter):
    def start(self):
        self.file.write('[')
        self.is_first_readings = True

    def write_readings(self, readings):
        if readings is None: return
        for reading in readings:
            if self.is_first_readings:
                self.is_first_readings = False
            else:
                self.file.write(',')
            self.file.write(json.dumps(reading))

    def finish(self):
        self.file.write(']')
