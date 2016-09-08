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
    org = client.authorized_organization()
    org = org.update(name=name)
    Organization.display(client, [org])


@cli.command()
@pass_client
def user(client):
    """Lists users for the organization.

    Lists the users that are part of the authorized organization.
    """
    org = Organization.singleton(client, include=[User])
    User.display(client, org.users(use_included=True))


@cli.command()
@pass_client
def element(client):
    """Lists elements for the organization.

    Lists the elements that are part of the authorized organization.
    """
    org = Organization.singleton(client, include=[Element])
    Element.display(client, org.elements(use_included=True))


@cli.command()
@pass_client
def sensor(client):
    """Lists senors for the organization.

    Lists the sensors that are part of the authorized organization.
    """
    org = Organization.singleton(client, include=[Sensor])
    Element.display(client, org.sensors(use_included=True))
