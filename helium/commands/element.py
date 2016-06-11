import click
import util
import helium
import helium.commands.sensor as _sensor
import dpath.util as dpath

pass_service=click.make_pass_decorator(helium.Service)

def _find_element_id(service, element):
    return util.lookup_resource_id(service.get_elements, element)


@click.group()
def cli():
    """Operations on elements.
    """
    pass

def _tabulate(result, **kwargs):
    def _map_sensor_count(json):
        return len(dpath.get(json, 'relationships/sensor/data'))
    version_map = []
    version_option = kwargs.pop('versions', 'none')
    if version_option == 'fw':
        version_map = [
            ('firmware', 'meta/versions/element'),
        ]
    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('mac', 'meta/mac'),
        ('sensors', _map_sensor_count)
    ] +  version_map + [
        ('name', 'attributes/name')
    ])


@cli.command()
@click.argument('element',required=False)
@click.option('--versions', type=click.Choice(['none', 'fw']),
              default='none',
              help="display element version information")
@pass_service
def list(service, element, **kwargs):
    """List elements.

    Lists one or all elements in the organization.
    """
    if element:
        element = _find_element_id(service, element)
        elements=[service.get_element(element, include='sensor').get('data')]
    else:
        elements=service.get_elements(include='sensor').get('data')
    _tabulate(elements, **kwargs)


@cli.command()
@click.argument('element')
@click.option('--name',
              help="the new name for the sensor")
@pass_service
def update(service, element, **kwargs):
    """Updates the attributes of an element.

    Updates the attributes of a given ELEMENT.
    """
    element = _find_element_id(service, element)
    data = service.update_element(element, **kwargs).get('data')
    _tabulate([data])


@cli.command()
@click.argument('element')
@_sensor.version_option
@pass_service
def sensor(service, element, **kwargs):
    """Lists sensors for an element.

    Lists the sensors for a given ELEMENT.
    """
    element = _find_element_id(service, element)
    sensors = service.get_element(element, include='sensor').get('included')
    _sensor._tabulate(sensors, **kwargs)
