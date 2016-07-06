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


def _find_sensor_id(service, sensor, **kwargs):
    return lookup_resource_id(service.get_sensors, sensor, **kwargs)


def _tabulate(result, **kwargs):
    version_map = []
    version_base = [
        ('atom', 'meta/versions/atom'),
        ('firmware', 'meta/versions/sensor'),
    ]
    version_option = kwargs.pop('versions', 'none')
    if version_option == 'fw':
        version_map = version_base
    elif version_option == 'all':
        def _map_script_versions(json):
            versions = dpath.values(json, 'meta/versions/sensor-script/*/version')
            return '\n'.join([v for v in versions if not v.startswith('ffffffff')])
        version_map = version_base + [
            ('libary', 'meta/versions/sensor-library'),
            ('config', 'meta/versions/sensor-config'),
            ('script', _map_script_versions)
        ]

    def _map_card(json):
        key = unicode(dpath.get(json, 'meta/card/id'))
        return card_type(key, key)

    tabulate(result, [
        ('id', shorten_json_id),
        ('mac', 'meta/mac'),
        ('type', _map_card),
        ('seen', 'meta/last-seen'),
    ] + version_map + [
        ('name', 'attributes/name'),
    ], **kwargs)


@cli.command()
@click.argument('sensor', required=False)
@click.option('-l', '--label', metavar='LABEL',
              help="the id of a label")
@version_option
@mac_option
@sort_option
@pass_service
def list(service, sensor, label, **kwargs):
    """List sensors.

    Lists information for a label of sensors or all sensors in
    the organization.
    """
    if label:
        label = lookup_resource_id(service.get_labels, label)
        sensors = service.get_label(label, include="sensor").get('included')
    elif sensor:
        sensor = _find_sensor_id(service, sensor, **kwargs)
        sensors = [service.get_sensor(sensor).get('data')]
    else:
        sensors = service.get_sensors().get('data')
    _tabulate(sensors, **kwargs)


@cli.command()
@click.option('--name', required=True,
              help="the name for the new virtual sensor")
@pass_service
def create(service, name):
    """Create a virtual sensor.

    Create a virtual sensor with a name.
    """
    sensors = [service.create_sensor(name=name).get('data')]
    _tabulate(sensors)


@cli.command()
@click.argument('sensor')
@click.option('--name',
              help="the new name for the sensor")
@mac_option
@pass_service
def update(service, sensor, **kwargs):
    """Updates the attributes of a sensor.

    Updates the attributes of a given SENSOR.
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    data = service.update_sensor(sensor, **kwargs).get('data')
    _tabulate([data])


@cli.command()
@click.argument('sensor')
@mac_option
@pass_service
def delete(service, sensor, **kwargs):
    """Delete a sensor.

    Deletes the SENSOR with the given id.
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    result = service.delete_sensor(sensor)
    click.echo("Deleted" if result.status_code == 204 else result)


@click.argument('sensor')
@mac_option
@pass_service
def _get_sensor_timeseries(service, sensor, **kwargs):
    """Get timeseries readings for a sensor.

    Retrieve timeseries data for a given SENSOR.
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    return service.get_sensor_timeseries(sensor, **kwargs).get('data')


@click.argument('sensor')
@mac_option
@pass_service
def _post_sensor_timeseries(service, sensor, **kwargs):
    """Post readings to a sensor.

    Posts timeseries readings for a given SENSOR.
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    return [service.post_sensor_timeseries(sensor, **kwargs).get('data')]


@click.argument('sensor')
@mac_option
@pass_service
def _live_sensor_timeseries(service, sensor, **kwargs):
    """Live readings from a sensor.

    Reports readings from a sensor as they come in.
    """
    sensor = _find_sensor_id(service, sensor, **kwargs)
    return service.live_sensor_timeseries(sensor, **kwargs)


cli.add_command(ts.cli(get=_get_sensor_timeseries,
                       post=_post_sensor_timeseries,
                       live=_live_sensor_timeseries))


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
