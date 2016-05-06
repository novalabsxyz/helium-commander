import click
import util
import helium

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on elements.
    """
    pass

def _tabulate(result):
    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name')
    ])


@cli.command()
@click.argument('element',required=False)
@pass_service
def list(service, element):
    """List elements.

    Lists one or all elements in the organization.
    """
    if element:
        element = util.lookup_resource_id(service.get_elements, element)
        elements=[service.get_element(element).get('data')]
    else:
        elements=service.get_elements().get('data')
    _tabulate(elements)


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
