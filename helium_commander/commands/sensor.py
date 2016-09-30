import click
from helium_commander import Client, Sensor
from helium_commander import device_mac_option, device_sort_option
from helium_commander.commands import timeseries


pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass


@cli.command()
@click.argument('sensor', required=False)
@device_mac_option
@device_sort_option
@pass_client
def list(client, sensor, mac, **kwargs):
    """List sensors.

    Lists information for a given SENSOR or all sensors in the
    organization.

    """
    if sensor:
        sensors = [Sensor.lookup(client, sensor, mac=mac)]
    else:
        sensors = Sensor.all(client)
    Sensor.display(client, sensors, **kwargs)


@cli.command()
@click.option('--name', required=True,
              help="the name for the new virtual sensor")
@pass_client
def create(client, name):
    """Create a virtual sensor.

    Create a virtual sensor with a name.
    """
    sensor = Sensor.create(client, name=name)
    Sensor.display(client, [sensor])


@cli.command()
@click.argument('sensor')
@click.option('--name',
              help="the new name for the sensor")
@device_mac_option
@pass_client
def update(client, sensor, name, mac, **kwargs):
    """Updates the attributes of a sensor.

    Updates the attributes of a given SENSOR.
    """
    sensor = Sensor.lookup(client, sensor, mac=mac)
    sensor = sensor.update(name=name)
    Sensor.display(client, [sensor])


@cli.command()
@click.argument('sensor')
@device_mac_option
@pass_client
def delete(client, sensor, mac, **kwargs):
    """Delete a sensor.

    Deletes the SENSOR with the given id.
    """
    sensor = Sensor.lookup(client, sensor, mac=mac)
    sensor.delete()
    click.echo("Deleted {}".format(sensor.id))


cli.add_command(timeseries.cli(Sensor))
