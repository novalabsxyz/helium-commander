import click
from helium_commander import (
    Client,
    Label,
    Sensor,
    Element,
    device_sort_option,
    device_mac_option,
    metadata_filter_option,
    ResourceParamType
)
from helium_commander.commands import metadata, timeseries
from collections import namedtuple


pass_client = click.make_pass_decorator(Client)
label_includes = [Sensor, Element]

LabelActionResources = namedtuple('LabelResourceActions',
                                  ['add', 'remove', 'replace'])


def lookup_label_action_resources(client, cls, mac=False, **kwargs):
    """Look up resources for a label."""
    def _lookup(action, resources):
        id_reps = kwargs.pop(action, None)
        if not id_reps:
            return None         # No change
        if 'none' in id_reps:
            return []           # Empty out the resources
        return [cls.lookup(client, id, resources=resources, mac=mac)
                for id in id_reps]

    all_resources = cls.all(client)
    return LabelActionResources(_lookup('add', all_resources),
                                _lookup('remove', all_resources),
                                _lookup('replace', all_resources))


@click.group()
def cli():
    """Operations on labels of sensors.
    """
    pass


@cli.command()
@click.argument('label', required=False)
@metadata_filter_option
@pass_client
def list(client, label, **kwargs):
    """List labels.

    Lists information for a given LABEL or all labels in the
    organization.

    """
    if label:
        labels = [Label.lookup(client, label, include=label_includes)]
    else:
        metadata = kwargs.get('metadata') or None
        labels = Label.where(client, include=label_includes, metadata=metadata)
    Label.display(client, labels, include=label_includes)


cli.add_command(timeseries.cli(Label, history=False,
                               writable=False, device=False))


@cli.command()
@click.argument('name')
@click.option('--sensors',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.option('--elements',
              type=ResourceParamType(metavar='ELEMENT'),
              help="Add elements to a label")
@click.pass_context
def create(ctx, name, sensors, elements):
    """Create a label.

    Creates a label with a given NAME and an (optional) list of
    sensors and elements associated with that label.

    """
    client = ctx.find_object(Client)

    sensors = sensors or []
    if sensors:
        all_sensors = Sensor.all(client)
        sensors = [Sensor.lookup(client, id, resources=all_sensors)
                   for id in sensors]

    elements = elements or []
    if elements:
        all_elements = Element.all(client)
        elements = [Element.lookup(client, id, resources=all_elements)
                    for id in elements]

    label = Label.create(client, attributes={
        'name': name
    })

    if sensors:
        label.update_sensors(sensors)

    if elements:
        label.update_elements(elements)

    label = Label.find(client, label.id, include=label_includes)
    Label.display(client, [label], include=label_includes)


@cli.command()
@click.argument('label', nargs=-1)
@pass_client
def delete(client, label):
    """Delete one or more labels.

    Deletes the LABELs with the given ids
    """
    all_labels = Label.all(client)
    label = [Label.lookup(client, id, resources=all_labels) for id in label]
    for entry in label:
        entry.delete()
        click.echo("Deleted {} ".format(entry.id))


@cli.command()
@click.argument('label')
@click.option('--name',
              help="the new name for the label")
@pass_client
def update(client, label, name):
    """Update a label.

    Changes basic attributes on a label.

    To add or remove sensors or elements from a label see the `label
    element` and `label sensor` commands.

    """
    label = Label.lookup(client, label)
    if name:
        label.update(attributes={
            'name': name
        })

    label = Label.find(client, label.id, include=label_includes)
    Label.display(client, [label], include=label_includes)


cli.add_command(metadata.cli(Label))


@cli.command()
@click.argument('label')
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.option('--remove',
              type=ResourceParamType(metavar='SENSOR'),
              help="Remove sensors from a label")
@click.option('--replace',
              type=ResourceParamType(metavar='SENSOR'),
              help="Replace all sensors in a label")
@device_sort_option
@device_mac_option
@pass_client
def sensor(client, label, mac, **kwargs):
    """List sensors for a label.

    List sensors for a given LABEL.

    Add, remove or replace sensors from the LABEL by using the --add,
    --remove or --replace arguments respectively. Note that you can
    specify "none" with these to indicate an empty list.

    """
    label = Label.lookup(client, label)

    actions = lookup_label_action_resources(client, Sensor,
                                            mac=mac, **kwargs)

    if actions.add is not None:
        label.add_sensors(actions.add)

    if actions.remove is not None:
        label.remove_sensors(actions.remove)

    if actions.replace is not None:
        label.update_sensors(actions.replace)

    sensors = label.sensors()
    Sensor.display(client, sensors, **kwargs)


@cli.command()
@click.argument('label')
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.option('--remove',
              type=ResourceParamType(metavar='SENSOR'),
              help="Remove sensors from a label")
@click.option('--replace',
              type=ResourceParamType(metavar='SENSOR'),
              help="Replace all sensors in a label")
@device_sort_option
@device_mac_option
@pass_client
def element(client, label, mac, **kwargs):
    """List elements for a label.

    List elements for a given LABEL.

    Add, remove or replace sensors from the LABEL by using the --add,
    --remove or --replace arguments respectively. Note that you can
    specify "none" with these to indicate an empty list.

    """
    label = Label.lookup(client, label)

    actions = lookup_label_action_resources(client, Element,
                                            mac=mac, **kwargs)

    if actions.add is not None:
        label.add_elements(actions.add)

    if actions.remove is not None:
        label.remove_elements(actions.remove)

    if actions.replace is not None:
        label.update_elements(actions.replace)

    elements = label.elements()
    Element.display(client, elements, **kwargs)
