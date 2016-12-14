import click
from helium_commander import Client, User
from collections import OrderedDict

pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operations on the authorized user.
    """
    pass


@cli.command()
@pass_client
def list(client):
    """Lists user information for the current user.

    Lists information associated withe the user for the current api key.
    """
    user = User.singleton(client)
    User.display(client, [user])


@cli.command()
@click.option('--name',
              help="the new name for the user")
@pass_client
def update(client, name):
    """Update the attributes of the user.

    Updates the attributes of the currently authorized user.
    """
    user = User.singleton(client)
    attributes = OrderedDict()
    if name:
        attributes['name'] = name
    user = user.update(attributes=attributes)
    User.display(client, [user])
