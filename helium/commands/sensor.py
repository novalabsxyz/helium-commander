import click
import helium
import util
import timeseries as ts
import dpath.util as dpath

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass

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

    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('mac', 'meta/mac'),
    ] + version_map + [
        ('name', 'attributes/name'),
    ])


@cli.command()
@click.option('-l', '--label',
              help="the id of a label")
@click.option('--versions', type=click.Choice(['none', 'fw', 'all']),
              default='none',
              help="display sensor version information")
@pass_service
def list(service, label, **kwargs):
    """List sensors.

    Lists information for a label of sensors or all sensors in
    the organization.
    """
    if label:
        label = util.lookup_resource_id(service.get_labels, label)
        sensors = service.get_label(label,include="sensor").get('included')
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
@pass_service
def update(service, sensor, **kwargs):
    """Updates the attributes of a sensor.

    Updates the attributes of a given SENSOR.
    """
    sensor = util.lookup_resource_id(service.get_sensors, sensor)
    data = service.update_sensor(sensor, **kwargs).get('data')
    _tabulate([data])


@cli.command()
@click.argument('sensor')
@pass_service
def delete(service, sensor):
    """Delete a sensor.

    Deletes the SENSOR with the given id.
    """
    sensor = util.lookup_resource_id(service.get_sensors, sensor)
    result = service.delete_sensor(sensor)
    click.echo("Deleted" if result.status_code == 204 else result)


@cli.command()
@click.argument('sensor')
@ts.options()
@pass_service
def timeseries(service, sensor, **kwargs):
    """List readings for a sensor.

    Lists one page of readings or aggregations of readings for a given SENSOR.
    """
    sensor = util.lookup_resource_id(service.get_sensors, sensor)
    data = service.get_sensor_timeseries(sensor, **kwargs).get('data')
    ts.tabulate(data, **kwargs)


@cli.command()
@ts.format_option()
@click.argument('sensor')
@ts.options(page_size=5000)
@pass_service
def dump(service, sensor, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for one SENSOR to a file.
    If no sensors or label is specified all sensors for the organization are dumped.

    One file is generated with the sensor id as filename and the
    file extension based on the requested dump format
    """
    sensor = util.lookup_resource_id(service.get_sensors, sensor)
    ts.dump(service, [sensor], format, **kwargs)
