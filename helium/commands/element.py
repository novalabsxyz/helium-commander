import click
import helium
from .sensor import version_option as sensor_version_option
from .sensor import mac_option, sort_option as sensor_sort_option
from .sensor import _tabulate as _tabulate_sensors
from .util import tabulate, lookup_resource_id, shorten_json_id
from .util import sort_option as _sort_option
import dpath.util as dpath

pass_service = click.make_pass_decorator(helium.Service)


def version_option(f):
    return click.option('--versions', type=click.Choice(['none', 'fw']),
                        default='none',
                        help="display version information")(f)


def sort_option(f):
    return _sort_option(['name'])(f)


@click.group()
def cli():
    """Operations on elements.
    """
    pass


def _find_element_id(service, element, **kwargs):
    return lookup_resource_id(service.get_elements, element, **kwargs)


def _tabulate(result, **kwargs):
    def _map_sensor_count(json):
        return len(dpath.get(json, 'relationships/sensor/data'))
    version_map = []
    version_option = kwargs.pop('versions', 'none')
    if version_option == 'fw':
        version_map = [
            ('firmware', 'meta/versions/element'),
        ]
    tabulate(result, [
        ('id', shorten_json_id),
        ('mac', 'meta/mac'),
        ('sensors', _map_sensor_count)
    ] + version_map + [
        ('name', 'attributes/name')
    ], **kwargs)


@cli.command()
@click.argument('element', required=False)
@version_option
@mac_option
@sort_option
@pass_service
def list(service, element, **kwargs):
    """List elements.

    Lists one or all elements in the organization.
    """
    if element:
        element = _find_element_id(service, element, **kwargs)
        elements = [service.get_element(element, include='sensor').get('data')]
    else:
        elements = service.get_elements(include='sensor').get('data')
    _tabulate(elements, **kwargs)


@cli.command()
@click.argument('element')
@click.option('--name',
              help="the new name for the sensor")
@mac_option
@pass_service
def update(service, element, **kwargs):
    """Updates the attributes of an element.

    Updates the attributes of a given ELEMENT.
    """
    element = _find_element_id(service, element, **kwargs)
    data = service.update_element(element, **kwargs).get('data')
    _tabulate([data])


@cli.command()
@click.argument('element')
@sensor_version_option
@sensor_sort_option
@mac_option
@pass_service
def sensor(service, element, **kwargs):
    """Lists sensors for an element.

    Lists the sensors for a given ELEMENT.
    """
    element = _find_element_id(service, element, **kwargs)
    sensors = service.get_element(element, include='sensor').get('included')
    _tabulate_sensors(sensors, **kwargs)
