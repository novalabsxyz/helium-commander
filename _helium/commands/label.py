import helium
import click
import dpath.util as dpath
from .timeseries import options as timeseries_options
from .timeseries import dump as timeseries_dump
from .sensor import sort_option as sensor_sort_option
from .sensor import _tabulate as _tabulate_sensors
from .util import tabulate, lookup_resource_id, shorten_json_id
from .util import ResourceParamType, update_resource_relationship


pass_service = click.make_pass_decorator(helium.Service)


@click.group()
def cli():
    """Operations on labels of sensors.
    """
    pass


@cli.command()
@click.argument('label')
@timeseries_options()
@pass_service
def dump(service, label, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for all sensors in a given LABEL.

    One file is generated for each sensor with the sensor id as
    filename and the file extension based on the requested dump format

    """
    label = lookup_resource_id(service.get_labels, label)
    sensors = dpath.values(service.get_label_sensors(label), '/data/*/id')
    timeseries_dump(service, sensors, **kwargs)
