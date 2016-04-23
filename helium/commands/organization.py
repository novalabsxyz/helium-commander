import click
import helium
import dpath.util as dpath
import timeseries as ts


pass_service=click.make_pass_decorator(helium.Service)

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
    Readings can be filtered by PORT and by START and END date. Dates are given
    in ISO-8601 and may be one of the following forms:

    \b
    * YYYY-MM-DD - Example: 2016-05-05
    * YYYY-MM-DDTHH:MM:SSZ - Example: 2016-04-07T19:12:06Z
    """
    data = service.get_org_timeseries(**kwargs).get('data')
    ts.tabulate(data)


@cli.command()
@ts.format_option()
@ts.options(page_size=5000)
@pass_service
def dump(service, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for all sensors in the organization.

    One file is generated for each sensor with the sensor id as filename and the
    file extension based on the requested dump format

    This command takes the same arguments as the `timeseries` command, including
    the ability to filter by PORT, START and END date
    """
    sensors = dpath.values(service.get_sensors(), '/data/*/id')
    ts.dump(service, sensors, format, **kwargs)
