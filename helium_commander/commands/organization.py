import click
from helium_commander import Client, Organization
from helium_commander import User, Element, Sensor, Label
from helium_commander.commands import timeseries
from helium_commander.commands import metadata
from collections import OrderedDict

pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operations on the authorized organization
    """
    pass


@cli.command()
@pass_client
def list(client):
    """Display basic information of the organization.

    Displays basic attributes of the authorized organization.
    """
    include = [User, Element, Sensor]
    org = Organization.singleton(client, include=include)
    Organization.display(client, [org], include=include)


supported_timezones = [
    'UTC',
    'US/Pacific',
    'US/Eastern',
    'US/Central',
    'US/Mountain',
    'US/Pacific',
    'Europe/London'
]


@cli.command()
@click.option('--name',
              help="the new name for the organization")
@click.option('--timezone', type=click.Choice(supported_timezones),
              help="the timezone for the organization")
@pass_client
def update(client, name, timezone):
    """Update the attributes of the organization.

    Updates the attributes of the currently authorized organization.
    """
    org = Organization.singleton(client)
    attributes = OrderedDict()
    if name:
        attributes['name'] = name
    if timezone:
        attributes['timezone'] = timezone
    org = org.update(attributes=attributes)
    include = [User, Element, Sensor]
    org = Organization.singleton(client, include=include)
    Organization.display(client, [org], include=include)


@cli.command()
@pass_client
def sensor(client):
    """List sensors for the organization.

    Lists all sensors for the authorized organization.
    """
    org = Organization.singleton(client)
    Sensor.display(client, org.sensors())


@cli.command()
@pass_client
def element(client):
    """List elements for the organization.

    Lists all elements for the authorized organization.
    """
    org = Organization.singleton(client)
    Element.display(client, org.elements())


@cli.command()
@pass_client
def user(client):
    """List users for the organization.

    Lists all users for the authorized organization.
    """
    org = Organization.singleton(client)
    User.display(client, org.users())


@cli.command()
@pass_client
def label(client):
    """List labels for the organization.

    Lists all labels for the authorized organization.
    """
    org = Organization.singleton(client)
    Label.display(client, org.labels())


cli.add_command(timeseries.cli(Organization, singleton=True))
cli.add_command(metadata.cli(Organization, singleton=True))
