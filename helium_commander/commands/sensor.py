import click
from helium_commander import (
    Client,
    Sensor,
    Element,
    device_mac_option,
    device_sort_option,
    metadata_filter_option
)
from helium_commander.commands import timeseries, metadata


pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operate on physical or virtual sensors.
    """
    pass


@cli.command()
@click.argument('sensor', required=False)
@device_mac_option
@device_sort_option
@metadata_filter_option
@pass_client
def list(client, sensor, mac, **kwargs):
    """List sensors.

    Lists information for a given SENSOR or all sensors in the
    organization.

    """
    if sensor:
        sensors = [Sensor.lookup(client, sensor, mac=mac)]
    else:
        metadata = kwargs.get('metadata') or None
        sensors = Sensor.where(client, metadata=metadata)
    Sensor.display(client, sensors, **kwargs)


@cli.command()
@click.option('--name', required=True,
              help="the name for the new virtual sensor")
@pass_client
def create(client, name):
    """Create a virtual sensor.

    Create a virtual sensor with a name.
    """
    sensor = Sensor.create(client, attributes={
        'name': name
    })
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
    sensor = sensor.update(attributes={
        'name': name
    })
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
cli.add_command(metadata.cli(Sensor))


@cli.command()
@click.argument('sensor')
@device_mac_option
@pass_client
def element(client, sensor, mac):
    """Get the element for a sensor.

    Gets the element a given SENSOR was last seen connected to.
    """
    sensor = Sensor.lookup(client, sensor, mac=mac, include=[Element])
    element = sensor.element(use_included=True)
    Element.display(client, [element] if element else [])


@cli.command()
@click.argument('sensor')
@device_mac_option
@pass_client
def label(client, sensor, mac):
    """Get the labels for a sensor.

    Gets all the labels that a given SENSOR is part of.
    """
    sensor = Sensor.lookup(client, sensor, mac=mac)
    Sensor.display(client, sensor.labels())
