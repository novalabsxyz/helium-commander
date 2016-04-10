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
    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name')
    ]))


@cli.command()
@click.argument('element',required=False)
@pass_service
def list(service, element):
    """List elements.

    Lists one or all elements in the organization.
    """
    if element:
        elements=[service.get_element(element).get('data')]
    else:
        elements=service.get_elements().get('data')
    _tabulate(elements)
