import click
import helium
import util
import timeseries as ts

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on physical or virtual sensors.
    """
    pass

def _tabulate(result):
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name'),
    ]))

@cli.command()
@click.option('-l', '--label',
              help="the id of a label")
@pass_service
def list(service, label):
    """List sensors.

    Lists information for a label of sensors or all sensors in
    the organization.
    """
    if label:
        sensors = service.get_label(label,include="sensor").get('included')
    else:
        sensors = service.get_sensors().get('data')
    _tabulate(sensors)


@cli.command()
@click.option('-n', '--name', required=True,
              help="the name for the new virtual sensor")
@pass_service
def create(service, name):
    """Create a virtual sensor.

    Create a virtual sensor with a name.
    """
    sensors = [service.create_sensor(name).get('data')]
    _tabulate(sensors)


@cli.command()
@click.argument('sensor')
@pass_service
def delete(service, sensor):
    """Delete a sensor.

    Deletes the SENSOR with the given id.
    """
    result = service.delete_sensor(sensor)
    click.echo("Deleted" if result.status_code == 204 else result)


@cli.command()
@click.argument('sensor')
@ts.options()
@pass_service
def timeseries(service, sensor, **kwargs):
    """List readings for a sensor.

    Lists one page of readings for a given SENSOR.
    Readings can be filtered by PORT and by START and END date. Dates are given
    in ISO-8601 and may be one of the following forms:

    \b
    * YYYY-MM-DD - Example: 2016-05-05
    * YYYY-MM-DDTHH:MM:SSZ - Example: 2016-04-07T19:12:06Z

    """
    data = service.get_sensor_timeseries(sensor, **kwargs).get('data')
    ts.tabulate(data)


@cli.command()
@ts.format_option()
@click.argument('sensor')
@ts.options(page_size=5000)
@pass_service
def dump(service, sensor, format, **kwargs):
    """Dumps timeseries data to files.

    Dumps the timeseries data for one SENSOR to a file.
    If no sensors or label is specified all sensors for the organization are dumped.

    One file is generated with the sensor id as filename and the
    file extension based on the requested dump format

    This command takes the same arguments as the `timeseries` command, including
    the ability to filter by PORT, START and END date
    """
    ts.dump(service, [sensor], format, **kwargs)
