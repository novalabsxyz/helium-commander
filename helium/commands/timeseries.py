import helium
import click
import sys
from json import loads as load_json
from concurrent import futures
from functools import update_wrapper
from .util import shorten_json_id, tabulate, output_format
from .writer import for_format as writer_for_format
from contextlib import closing


def cli(get=None, post=None, live=None):
    def tabulating_decorator(f):
        def new_func(*args, **kwargs):
            ctx = click.get_current_context()
            data = ctx.invoke(f, *args, **kwargs)
            _tabulate(data, **kwargs)
            return data
        return update_wrapper(new_func, f)

    def live_decorator(f):
        def new_func(*args, **kwargs):
            ctx = click.get_current_context()
            with writer_for_format(output_format(default_format='json', **kwargs),
                                   click.utils.get_text_stream('stdout'),
                                   mapping=_mapping_for(**kwargs)) as _writer:
                with closing(ctx.invoke(f, *args, **kwargs)) as live:
                    for type, data in live.events():
                        data = data.get('data')
                        _writer.write_entries([data])
        return update_wrapper(new_func, f)

    group = click.Group(name='timeseries',
                        short_help="Commands on timeseries readings.")

    # List
    # Create options, wrapping the tabulating getter
    list_params = getattr(get, '__click_params__', [])
    get.__click_params__ = []
    options_get = options()(tabulating_decorator(get))
    # then construct the actual list command
    list_command = click.command('list')(options_get)
    list_command.params = list_params + list_command.params
    group.add_command(list_command)

    # Post
    # Pull of any parameters from the given poster since we want them
    # at the head of the other post parameters
    post_params = getattr(post, '__click_params__', [])
    post.__click_params__ = []
    # Construct the post options wrapping the tabulating poster
    options_post = post_options()(tabulating_decorator(post))
    post_command = click.command('post')(options_post)
    # and prefix the poster's parameters
    post_command.params = post_params + post_command.params
    group.add_command(post_command)

    # Live
    live_command = click.command('live')(live_decorator(live))
    group.add_command(live_command)

    return group


_options_docs = """
    Readings can be filtered by PORT and by START and END date and can
    be aggregated given an aggregation type and aggregation window size.

    Dates are given in ISO-8601 and may be one of the following forms:

    \b
    * YYYY-MM-DD - Example: 2016-05-05
    * YYYY-MM-DDTHH:MM:SSZ - Example: 2016-04-07T19:12:06Z

    Aggregations or bucketing of data can be done by specifying
    the size of each aggregation bucket using agg-size
    and one of the size specifiers.

    \b
    Examples: 1m, 2m, 5m, 10m, 30m, 1h, 1d

    How data-points are aggregated is indicated by a list of
    aggregation types using agg-type.

    \b
    Examples: min, max, avg

    For example, to aggregate min, max for a specific port 't' and
    aggregate on a daily basis use the following:

    \b
    --agg-type min,max --agg-size 1d --port t
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
                     help="the kinds of aggregations to perform"),
    ]

    def wrapper(func):
        func.__doc__ += _options_docs
        for option in reversed(options):
            func = option(func)
        return func
    return wrapper


_post_options_docs = """
    The given VALUE is inserted to the timeseries stream using the given PORT.

    The optional timestamp option allows fine grained control over the date of
    the reading and can be given in ISO8601 form:

    \b
    * YYYY-MM-DD - Example: 2016-05-05
    * YYYY-MM-DDTHH:MM:SSZ - Example: 2016-04-07T19:12:06Z
"""


def post_options():
    """Standard arguments and options for posting timeseries readings.
    """
    options = [
        click.argument('port'),
        click.argument('value', type=JSONParamType()),
        click.option('--timestamp', metavar='DATE',
                     help='the time of the reading'),
    ]

    def wrapper(func):
        func.__doc__ += _post_options_docs
        for option in reversed(options):
            func = option(func)
        return func
    return wrapper


class JSONParamType(click.ParamType):
    name = 'JSON'

    def convert(self, value, param, ctx):
        try:
            return load_json(value)
        except ValueError:
            self.fail('{} is not a valid json value'.format(value), param, ctx)


def _mapping_for(uuid=False, **kwargs):
    agg_types = kwargs.pop('agg_type', None)
    if agg_types:
        agg_types = agg_types.split(',')
        value_map = [(key, "attributes/value/" + key) for key in agg_types]
    else:
        value_map = [('value', 'attributes/value')]
    map = [
        ('id', shorten_json_id if not uuid else 'id'),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port')
    ] + value_map
    return map


def _tabulate(result, **kwargs):
    if not result:
        click.echo('No data')
        return
    tabulate(result, _mapping_for(**kwargs))


def dump(service, sensors, **kwargs):
    label = str.format("Dumping {}", len(sensors))
    with click.progressbar(length=len(sensors),
                           label=label,
                           show_eta=False,
                           width=50) as bar:
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            all_futures = []
            format = output_format('csv')
            for sensor_id in sensors:
                future = executor.submit(_dump_one, service, sensor_id, format,
                                         **kwargs)
                future.add_done_callback(lambda f: bar.update(1))
                all_futures.append(future)
                # Pass in timeout to wait to enable keyboard abort
                # (Python 2.7 issue)
            result_futures = futures.wait(all_futures,
                                          return_when=futures.FIRST_EXCEPTION,
                                          timeout=sys.maxint)
            for future in result_futures.done:
                future.result()  # re-raises the exception


def _process_timeseries(writer, service, sensor_id, **kwargs):
    def json_data(json):
        return json['data'] if json else None
    # Get the first page
    res = service.get_sensor_timeseries(sensor_id, **kwargs)
    writer.start()
    writer.write_entries(json_data(res))
    while res is not None:
        res = service.get_prev_page(res)
        writer.write_entries(json_data(res))
        writer.finish()


def _dump_one(service, sensor_id, format, **kwargs):
    filename = (sensor_id+'.'+format).encode('ascii', 'replace')
    with click.open_file(filename, "wb") as file:
        csv_mapping = _mapping_for(shorten_json_id=False, **kwargs)
        service = helium.Service(service.api_key, service.base_url)
        output = writer_for_format(format, file, mapping=csv_mapping)
        _process_timeseries(output, service, sensor_id, **kwargs)
