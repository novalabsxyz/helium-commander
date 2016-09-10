import click

from itertools import islice
from helium_commander import Client, DataPoint
from helium_commander import JSONParamType

pass_client = click.make_pass_decorator(Client)


def cli(cls, lookup_options=None):
    group = click.Group(name='timeseries',
                        short_help="Commands on timeseries readings.")
    resource_type = cls._resource_type()

    @group.command('list')
    @click.argument('id', metavar=resource_type)
    @list_options()
    @pass_client
    def _list(client, id, **kwargs):
        """Get timeseries readings."""
        mac = kwargs.pop('mac', False)
        resource = cls.lookup(client, id, mac=mac)
        timeseries = resource.timeseries(**kwargs)
        timeseries = islice(timeseries, kwargs.get('page_size', 20))
        DataPoint.display(client, timeseries, **kwargs)

    @group.command('post')
    @click.argument('id', metavar=resource_type)
    @post_options()
    @pass_client
    def _post(client, id, **kwargs):
        """Post timeseries readings."""
        mac = kwargs.pop('mac', False)
        resource = cls.lookup(client, id, mac=mac)
        timeseries = resource.timeseries()
        point = timeseries.post(**kwargs)
        DataPoint.display(client, [point], **kwargs)

    @group.command('live')
    @click.argument('id', metavar=resource_type)
    @list_options()
    @pass_client
    def _live(client, id, **kwargs):
        """Get live timeseries readings"""
        mac = kwargs.pop('mac', False)
        resource = cls.lookup(client, id, mac=mac)
        timeseries = resource.timeseries(**kwargs)
        mapping = cls.display_map(client)
        with cls.display_writer(client, mapping, **kwargs) as writer:
            for data_point in timeseries.live():
                writer.write_resources([data_point])

    return group


_list_options_docs = """
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


def list_options(page_size=20):
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
        func.__doc__ += _list_options_docs
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
