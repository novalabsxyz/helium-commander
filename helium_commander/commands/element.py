import click
from helium_commander import Client, Element, Sensor
from helium_commander import device_mac_option, device_sort_option
from helium_commander.commands import timeseries


pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass


@cli.command()
@click.argument('element', required=False)
@device_mac_option
@device_sort_option
@pass_client
def list(client, element, mac, **kwargs):
    """List elements.

    Lists information for a given ELEMENT or all elements in the
    organization.

    """
    include = [Sensor]
    if element:
        elements = [Element.lookup(client, element, mac=mac, include=include)]
    else:
        elements = Element.all(client, include=include)
    Element.display(client, elements, include=include)


@cli.command()
@click.argument('element')
@click.option('--name',
              help="the new name for the element")
@device_mac_option
@pass_client
def update(client, element, name, mac, **kwargs):
    """Updates the attributes of a element.

    Updates the attributes of a given ELEMENT.
    """
    element = Element.lookup(client, element, mac=mac)
    element = element.update(name=name)
    include = [Sensor]
    element = Element.lookup(client, element.id, mac=mac, include=include)
    Element.display(client, [element], include=include)


cli.add_command(timeseries.cli(Element))


@cli.command()
@click.argument('element')
@device_mac_option
@device_sort_option
@pass_client
def sensor(client, element, mac, **kwargs):
    """Get the sensors for an element.

    Gets the sensors last known to be connected to a given ELEMENT.

    """
    element = Element.lookup(client, element, mac=mac, include=[Sensor])
    sensors = element.sensors(use_included=True)
    Sensor.display(client, sensors, **kwargs)
