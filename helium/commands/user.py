import click
import helium
import util
import dpath.util as dpath

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on the user.
    """
    pass

def _tabulate(result):
    util.tabulate(result, [
        ('id', 'id'),
        ('name', 'attributes/name')
    ])


@cli.command()
@pass_service
def list(service):
    """Lists user information for the current user.

    Lists information associated withe the user for the current api key.
    """
    _tabulate([service.get_user().get('data')])


@cli.command()
@click.argument('user')
@click.password_option(confirmation_prompt=False)
@pass_service
def auth(service, user, password):
    """Authenticates the given user and password.

    Authenticates the given USER and password.
    If successful the API key for the account is printed
    """
    result = service.auth_user(user, password).get('data')
    click.echo(dpath.get(result,'meta/api-token'))
