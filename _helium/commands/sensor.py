import click
import helium
import dpath.util as dpath
from . import timeseries as ts
from .util import tabulate, lookup_resource_id, shorten_json_id
from .util import sort_option as _sort_option


pass_service = click.make_pass_decorator(helium.Service)


def version_option(f):
    return click.option('--versions', type=click.Choice(['none', 'fw', 'all']),
                        default='none',
                        help="display version information")(f)


def sort_option(f):
    return _sort_option(['seen', 'name'])(f)


def mac_option(f):
    return click.option('--mac', is_flag=True,
                        help="Whether the given id is a mac address")(f)


def card_type(card_id, default):
    return {
        '2': 'blue',
        '5': 'green',
    }.get(card_id, default)


@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass


@cli.command()
@click.argument('sensor')
@ts.options(page_size=5000)
@mac_option
@pass_service
def dump(service, sensor, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for one SENSOR to a file.
    If no sensors or label is specified all sensors for the organization
    are dumped.

    One file is generated with the sensor id as filename and the
    file extension based on the requested dump format
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    ts.dump(service, [sensor], **kwargs)
