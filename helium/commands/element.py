import click
import util
import helium

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on elements.
    """
    pass

def _tabulate(result, **kwargs):
    version_map = []
    version_option = kwargs.pop('versions', 'none')
    if version_option == 'fw':
        version_map = [
            ('firmware', 'meta/versions/element'),
        ]
    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('mac', 'meta/mac'),
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
        element = util.lookup_resource_id(service.get_elements, element)
        elements=[service.get_element(element).get('data')]
    else:
        elements=service.get_elements().get('data')
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
    sensor = util.lookup_resource_id(service.get_elements, element)
    data = service.update_element(sensor, **kwargs).get('data')
    _tabulate([data])
