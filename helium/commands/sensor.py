import click
import helium
import util

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass

def _tabulate(result):
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name'),
    ]))

@cli.command()
@click.option('-l', '--label',
              help="the id of a label")
@pass_service
def list(service, label):
    """List sensors.

    Lists information for a label of sensors or all sensors in
    the organization.
    """
    if label:
        sensors = service.get_label(label,include="sensor").get('included')
    else:
        sensors = service.get_sensors().get('data')
    _tabulate(sensors)


@cli.command()
@click.option('-n', '--name', required=True,
              help="the name for the new virtual sensor")
@pass_service
def create(service, name):
    """Create a virtual sensor.

    Create a virtual sensor with a name.
    """
    sensors = [service.create_sensor(name).get('data')]
    _tabulate(sensors)


@cli.command(short_help="delete a sensor")
@click.argument('sensor')
@pass_service
def delete(service, sensor):
    """Delete a sensor.

    Deletes the SENSOR with the given id.
    """
    result = service.delete_sensor(sensor)
    click.echo("Deleted" if result.status_code == 204 else result)
