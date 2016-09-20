import click
from helium_commander import Client, Organization
from helium_commander import User, Element, Sensor
from helium_commander.commands import timeseries


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
    org = Organization.singleton(client, include=[User, Element, Sensor])
    Organization.display(client, [org])


@cli.command()
@click.option('--name',
              help="the new name for the organization")
@pass_client
def update(client, name):
    """Updates the attributes of the organization.

    Updates the attributes of the currently authorized organization.
    """
    org = Organization.singleton(client)
    org = org.update(name=name)
    org = Organization.singleton(client, include=[User, Element, Sensor])
    Organization.display(client, [org])


cli.add_command(timeseries.cli(Organization, singleton=True))
