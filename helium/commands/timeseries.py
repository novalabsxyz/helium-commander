from concurrent import futures
from collections import OrderedDict
import helium
import click
import util
import writer

def format_option():
    options = [
        click.option('--format', type=click.Choice(['csv', 'json']), default='csv',
                     help="the format of the readings (default 'csv')")
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
    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port'),
        ('value', 'attributes/value')
    ])


def dump(service, sensors, format, **kwargs):
    label = str.format("Dumping {}", len(sensors))
    with click.progressbar(length=len(sensors), label=label, show_eta=False, width=50) as bar:
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            all_futures = []
            for sensor_id in sensors:
                future = executor.submit(_dump_one, service, sensor_id, format, **kwargs)
                future.add_done_callback(lambda f: bar.update(1))
                all_futures.append(future)
            # Pass in timeout to wait to enable keyboard abort (Python 2.7 issue)
            result_futures = futures.wait(all_futures,
                                          return_when=futures.FIRST_EXCEPTION,
                                          timeout=sys.maxint)
            for future in result_futures.done:
                future.result() # re-raises the exception

def _process_timeseries(writer, service, sensor_id, **kwargs):
    def json_data(json):
        return json['data'] if json else None
    # Get the first page
    res = service.get_sensor_timeseries(sensor_id, **kwargs)
    writer.start()
    writer.write_entries(json_data(res))
    while res != None:
        res = service.get_prev_page(res)
        writer.write_entries(json_data(res))
    writer.finish()

def _dump_one(service, sensor_id, format, **kwargs):
    filename = (sensor_id+'.'+format).encode('ascii', 'replace')
    with click.open_file(filename, "wb") as file:
        csv_mapping = OrderedDict([
            ('id', 'id'),
            ('sensor', 'relationships/sensor/data/id'),
            ('timestamp', 'attributes/timestamp'),
            ('port', 'attributes/port'),
            ('value', 'attributes/value')
        ])
        service = helium.Service(service.api_key, service.base_url)
        output = writer.for_format(format, file, mapping=csv_mapping)
        _process_timeseries(output, service, sensor_id, **kwargs)
