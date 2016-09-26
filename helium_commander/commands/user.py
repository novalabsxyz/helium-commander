import click
from helium_commander import Client, User


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
@click.argument('email')
@click.argument('password')
@pass_client
def auth(client, email, password):     # pragma: no cover
    """Authenticate a user.

    Authenticates the given EMAIL and PASSWORD and displays the api key.
    """
    user = User.authenticate(client, email, password)
    click.echo(user.meta.api_token)
