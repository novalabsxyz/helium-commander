from concurrent import futures
import _dump_writer as _dump
import dpath.util as dpath
import helium
import click
import util

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on timeseries data
    """
    pass

def _tabulate(result):
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('timestamp', 'attributes/timestamp'),
        ('port', 'attributes/port'),
        ('value', 'attributes/value')
    ]))

def _dump_timeseries(service, sensor_id, format, page_size, port):
    filename = (sensor_id+'.'+format).encode('ascii', 'replace')
    with click.open_file(filename, "wb") as file:
        csv_mapping = {
            'id': 'id',
            'sensor': 'relationships/sensor/data/id',
            'timestamp': 'attributes/timestamp',
            'port': 'attributes/port',
            'value': 'attributes/value'
        }
        service = helium.Service(service.api_key)
        writer = _dump.writer_for_format(format, file, mapping=csv_mapping)
        writer.process_timeseries(service, sensor_id,
                                  port=port,
                                  page_size=page_size)


@cli.command()
@click.option('-f', '--format', type=click.Choice(['csv', 'json']), default='csv',
              help="the format of the readings")
@click.option('--page-size', default=1000,
              help="the number of readings to get")
@click.option('--port', multiple=True,
              help="the port to filter readings on")
@click.option('-l', '--label',
              help="the id for a label")
@click.argument('sensor', required=False, nargs=-1)
@pass_service
def dump(service, format, page_size, port, label, sensor):
    """Dump timeseries data to files.

    Dumps the timeseries data for one or more SENSORs or a label to files.
    If no sensors or label is specified all sensors for the organization are dumped.

    One file is generated for each sensor with the sensor id as filename and the
    file extension based on the requested dump format.
    """
    if sensor:
        sensors = sensor
    elif label:
        labels = service.get_label(label)
        sensors = dpath.values(labels, 'data/relationships/sensor/data/*/id')
    else:
        sensors = dpath.values(service.get_sensors(), '/data/*/id')

    with click.progressbar(length=len(sensors), label="Dumping", show_eta=False, width=50) as bar:
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            all_futures = []
            for sensor_id in sensors:
                future = executor.submit(_dump_timeseries, service, sensor_id, format, page_size, port)
                future.add_done_callback(lambda f: bar.update(1))
                all_futures.append(future)
            futures.wait(all_futures, return_when=FIRST_EXCEPTION)

@cli.command()
@click.argument('sensor', required=False)
@click.option('--page-size', default=20,
              help="the number of readings to get")
@click.option('--port', multiple=True,
              help="the port to filter readings on")
@pass_service
def list(service, sensor, page_size, port):
    """ List readings for a given sensor or the organization timeseries.

    List one page of readings for the given SENSOR. If SENSOR is not specified
    the organization timeseries is used as the source.
    """
    if sensor:
        data = service.get_sensor_timeseries(sensor, page_size=page_size, port=port).get("data")
    else:
        data = service.get_org_timeseries(page_size=page_size, port=port).get("data")
    _tabulate(data)
