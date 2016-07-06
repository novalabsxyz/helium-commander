import click
import helium
import dpath.util as dpath
from .util import tabulate
from . import timeseries as ts


pass_service = click.make_pass_decorator(helium.Service)


def _tabulate(result):
    def _map_user_count(json):
        return len(dpath.get(json, 'relationships/user/data'))
    tabulate(result, [
        ('id', 'id'),
        ('name', 'attributes/name'),
        ('users', _map_user_count)
    ])


def _tabulate_users(result):
    tabulate(result, [
        ('id', 'id')
    ])


@click.group()
def cli():
    """Operations on the authorized organization
    """
    pass


@pass_service
def _get_org_timeseries(service, **kwargs):
    """List readings for the organization.

    Get readings for the authenticated organization.
    """
    return service.get_org_timeseries(**kwargs).get('data')


@pass_service
def _post_org_timeseries(service, **kwargs):
    """Post readings to the organization.

    Posts timeseries to the authenticated organization.
    """
    return [service.post_org_timeseries(**kwargs).get('data')]

@pass_service
def _live_org_timeseries(service, **kwargs):
    """Live readings from the organization

    Reports readings from the authenticated organization as they come
    in.

    """
    return service.live_org_timeseries(**kwargs)


cli.add_command(ts.cli(get=_get_org_timeseries,
                       post=_post_org_timeseries,
                       live=_live_org_timeseries))


@cli.command()
@ts.options(page_size=5000)
@pass_service
def dump(service, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for all sensors in the organization.

    One file is generated for each sensor with the sensor id as
    filename and the file extension based on the requested dump format

    """
    sensors = dpath.values(service.get_sensors(), '/data/*/id')
    ts.dump(service, sensors, **kwargs)


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
    # TODO: Once include=user is supported fix up to display 'name'
    users = dpath.get(org, 'relationships/user/data')
    _tabulate_users(users)
