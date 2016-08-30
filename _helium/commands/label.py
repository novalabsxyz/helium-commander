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


def _tabulate(result, **kwargs):
    def _map_sensor_count(json):
        return len(dpath.get(json, 'relationships/sensor/data'))
    tabulate(result, [
        ('id', shorten_json_id),
        ('sensors', _map_sensor_count),
        ('name', 'attributes/name')
    ], **kwargs)


def _update_label_sensors(ctx, label, sensor, set_func):
    service = ctx.find_object(helium.Service)
    label = lookup_resource_id(service.get_labels, label)
    # Fetch the existing sensors
    sensors = service.get_label_sensors(label).get('data')
    sensor_ids = dpath.values(sensors, "*/id")
    # Look up full sensor ids for all given sensors
    sensor_list = [lookup_resource_id(service.get_sensors, sensor_id)
                   for sensor_id in sensor]
    # And perform the set operation and ensure we have a valid list
    sensor_ids = set_func(set(sensor_ids), set(sensor_list))
    if sensor_ids is None:
        sensor_ids = []
    service.update_label_sensors(label, sensor_ids)


@cli.command()
@click.argument('label', required=False)
@pass_service
def list(service, label, **kwargs):
    """Lists information on labels.

    Lists information on a given label or all labels in the organization
    """
    if label:
        label = lookup_resource_id(service.get_labels, label, **kwargs)
        result = [service.get_label(label, include='sensor').get('data')]
    else:
        result = service.get_labels(include='sensor').get('data')
    _tabulate(result, **kwargs)


@cli.command()
@click.argument('label')
@sensor_sort_option
@pass_service
def sensor(service, label, **kwargs):
    """Lists sensors for a label.

    Lists sensors for a given LABEL.
    """
    label = lookup_resource_id(service.get_labels, label, **kwargs)
    sensors = service.get_label(label, include='sensor').get('included')
    _tabulate_sensors(sensors, **kwargs)


@cli.command()
@click.argument('name')
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.pass_context
def create(ctx, name, **kwargs):
    """Create a label.

    Creates a label with a given NAME and an (optional) list of sensors
    associated with that label.
    """
    service = ctx.find_object(helium.Service)
    label = service.create_label(name).get('data')
    label = label['id']

    ctx.invoke(update, service, label=label, **kwargs)


@cli.command()
@click.argument('label', nargs=-1)
@pass_service
def delete(service, label):
    """Delete a label.

    Deletes the LABEL with the given id
    """
    label_list = service.get_labels().get('data')
    label = [lookup_resource_id(label_list, label_id)
             for label_id in label]
    for entry in label:
        result = service.delete_label(entry)
        click.echo("Deleted: " + entry
                   if result.status_code == 204 else result)


@cli.command()
@click.argument('label')
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.option('--remove',
              type=ResourceParamType(metavar='SENSOR'),
              help="Remove sensors from a label")
@click.option('--name',
              help="the new name for the label")
@pass_service
def update(service, label, name, **kwargs):
    label = lookup_resource_id(service.get_labels, label)
    org_sensors = service.get_sensors().get('data')

    def _label_sensors():
        return service.get_label(label, include='sensor').get('included')

    def _find_sensor_id(sensor, **kwargs):
        return lookup_resource_id(org_sensors, sensor, **kwargs)

    label_sensors = _label_sensors()
    label_sensor_ids = update_resource_relationship(label_sensors,
                                                    _find_sensor_id,
                                                    **kwargs)
    if name:
        service.update_label(label, name=name)
    if label_sensor_ids is not None:
        service.update_label_sensors(label, label_sensor_ids)
        label_sensors = _label_sensors()

    _tabulate([service.get_label(label, include='sensor').get('data')])


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
