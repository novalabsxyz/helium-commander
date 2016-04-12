import sensor
import helium
import util
import click
import dpath.util as dpath
import timeseries as ts

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on labels of sensors.
    """
    pass

def _tabulate(result):
    def _map_sensor_count(json):
        return len(dpath.get(json, 'relationships/sensor/data'))
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('name', 'attributes/name'),
        ('sensors', _map_sensor_count)
    ]))


@cli.command()
@click.argument('label',required=False)
@click.pass_context
def list(ctx, label):
    """Lists information on labels.

    Lists information on a given label or all labels in the organization
    """
    if label:
        ctx.invoke(sensor.list, label=label)
    else:
        service = ctx.find_object(helium.Service)
        _tabulate(service.get_labels(include='sensor').get('data'))


@cli.command()
@click.argument('name', nargs=1)
@click.argument('sensor', nargs=-1)
@pass_service
def create(service, name, sensor):
    """Create a label.

    Creates a label with a given NAME and an (optional) list of SENSORs
    associated with that label.
    """
    label = service.create_label(name).get('data')
    if sensor:
        service.update_label_sensors(label['id'], sensor)
    _tabulate([label])


@cli.command()
@click.argument('label')
@pass_service
def delete(service, label):
    """Delete a label.

    Deletes the LABEL with the given id
    """
    result = service.delete_label(label)
    click.echo("Deleted" if result.status_code == 204 else result)


@cli.command()
@click.argument('label',nargs=1)
@click.argument('sensor',nargs=-1)
@click.pass_context
def add(service, label, sensor):
    """Add sensors to a label.

    Adds a given list of SENSORs to the LABEL with the given id.
    """
    service = ctx.find_object(helium.Service)
    sensors = service.get_label_sensors(label).get('data')
    sensor_ids = dpath.values(sensors, "*/id")
    sensor_ids = set(sensor_ids).union(set(sensor))
    service.update_label_sensors(label, sensor_ids)
    ctx.invoke(sensor.list, label=label)


@cli.command()
@click.argument('label',nargs=1)
@click.argument('sensor',nargs=-1)
@pass_service
def remove(service, label, sensor):
    """Remove sensors from a label.

    Removes a given list of SENSORs from the LABEL with the given id.
    """
    service = ctx.find_object(helium.Service)
    sensors = service.get_label_sensors(label).get('data')
    sensor_ids = dpath.values(sensors, "*/id")
    sensor_ids = set(sensor_ids).difference(set(sensor))
    if sensor_ids is None: sensor_ids = []
    service.update_label_sensors(label, sensor_ids)
    ctx.invoke(sensor.list, label=label)


@cli.command()
@click.argument('label')
@ts.format_option()
@ts.options()
@pass_service
def dump(service, label, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for all sensors in a given LABEL.

    One file is generated for each sensor with the sensor id as filename and the
    file extension based on the requested dump format

    This command takes the same arguments as the `timeseries` command, including
    the ability to filter by PORT, START and END date
    """
    sensors = dpath.values(service.get_sensors(), '/data/*/id')
    ts.dump(service, sensors, format, **kwargs)
