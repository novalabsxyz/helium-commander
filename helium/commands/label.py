import sensor
import helium
import util
import click
import dpath.util as dpath

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
