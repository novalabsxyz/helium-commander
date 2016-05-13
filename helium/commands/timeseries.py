from concurrent import futures
from collections import OrderedDict
import helium
import click
import util
import sys
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

_options_docs = """
    Readings can be filtered by PORT and by START and END date and can
    be aggregated given an aggregation type and aggregation window size.

    Dates are given in ISO-8601 and may be one of the following forms:

    \b
    * YYYY-MM-DD - Example: 2016-05-05
    * YYYY-MM-DDTHH:MM:SSZ - Example: 2016-04-07T19:12:06Z
"""

def options(page_size=20):
    """Standard options for retrieving timeseries readings. In addition it
    appends the documentation for these options to the caller.

    The common usecase is to use this function as a decorator for a
    command like:

    \b
    ...
    @timeseries.options()
    def dump():
        ...
    """
    options = [
        click.option('--page-size', default=page_size,
                     help="the number of readings to get per request"),
        click.option('--port',
                     help="the port to filter readings on"),
        click.option('--start',
                     help="the start date to filter readings on"),
        click.option('--end',
                     help="the end date to filter readings on"),
        click.option('--agg-size',
                     help="the time window of the aggregation"),
        click.option('--agg-type',
                     help="the kinds of aggregations to perform")
    ]

    def wrapper(func):
        func.__doc__ += _options_docs
        for option in options:
            func = option(func)
        return func
    return wrapper


def _mapping_for(shorten_json_id=True, **kwargs):
    agg_types = kwargs.pop('agg_type')
    if agg_types:
        value_map = [(key, "attributes/value/" + key) for key in agg_types.split(',')]
    else:
        value_map = [('value', 'attributes/value')]
    map = [
        ('id', util.shorten_json_id if shorten_json_id  else 'id'),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port')
    ]
    map.extend(value_map)
    return map


def tabulate(result, **kwargs):
    if not result:
        click.echo('No data')
        return
    util.tabulate(result, _mapping_for(**kwargs))


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
        csv_mapping = OrderedDict(_mapping_for(shorten_json_id=False, **kwargs))
        service = helium.Service(service.api_key, service.base_url)
        output = writer.for_format(format, file, mapping=csv_mapping)
        _process_timeseries(output, service, sensor_id, **kwargs)
