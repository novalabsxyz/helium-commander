import click
import helium
import util
import dpath.util as dpath
import timeseries as ts


pass_service=click.make_pass_decorator(helium.Service)

def _tabulate(result):
    def _map_user_count(json):
        return len(dpath.get(json, 'relationships/user/data'))
    util.tabulate(result, [
        ('id', 'id'),
        ('name', 'attributes/name'),
        ('users', _map_user_count)
    ])

def _tabulate_users(result):
    util.tabulate(result, [
        ('id', 'id')
    ])

@click.group()
def cli():
    """Operations on the authorized organization
    """
    pass

@cli.command()
@ts.options()
@pass_service
def timeseries(service, **kwargs):
    """List readings for the organization.

    Lists one page of readings for the organization.
    """
    data = service.get_org_timeseries(**kwargs).get('data')
    ts.tabulate(data, **kwargs)


@cli.command()
@ts.format_option()
@ts.options(page_size=5000)
@pass_service
def dump(service, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for all sensors in the organization.

    One file is generated for each sensor with the sensor id as filename and the
    file extension based on the requested dump format
    """
    sensors = dpath.values(service.get_sensors(), '/data/*/id')
    ts.dump(service, sensors, format, **kwargs)


@cli.command()
@click.option('--name',
              help="the new name for the organization")
@pass_service
def update(service, **kwargs):
    """Updates the attributes of the organization.

    Updates the attributes of the currently authorized organization.
    """
    org = [service.update_org(**kwargs).get('data')]
    _tabulate(org)


@cli.command()
@pass_service
def list(service):
    """Display basic information of the organization.

    Displays basic attributes of the authorized organization.
    """
    org = [service.get_org().get('data')]
    _tabulate(org)


@cli.command()
@pass_service
def user(service):
    """Lists users for the organization.

    Lists the users that are part of the authorized organization.
    """
    org = service.get_org().get('data')
    ## TODO: Once include=user is supported fix up to display 'name'
    users = dpath.get(org, 'relationships/user/data')
    _tabulate_users(users)
