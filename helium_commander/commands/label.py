import click
from helium_commander import (
    Client,
    Label,
    Sensor,
    device_sort_option,
    metadata_filter_option,
    ResourceParamType
)
from helium_commander.commands import metadata, timeseries


pass_client = click.make_pass_decorator(Client)


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
    include = [Sensor]
    if label:
        labels = [Label.lookup(client, label, include=include)]
    else:
        metadata = kwargs.get('metadata') or None
        labels = Label.where(client, include=include, metadata=metadata)
    Label.display(client, labels, include=include)


cli.add_command(timeseries.cli(Label, history=False, writable=False))


@cli.command()
@click.argument('label')
@device_sort_option
@pass_client
def sensor(client, label, **kwargs):
    """Lists sensors for a label.

    Lists sensors for a given LABEL.
    """
    label = Label.lookup(client, label, include=[Sensor])
    sensors = label.sensors(use_included=True)
    Sensor.display(client, sensors, **kwargs)


@cli.command()
@click.argument('name')
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.pass_context
def create(ctx, name, **kwargs):
    """Create a label.

    Creates a label with a given NAME and an (optional) list of sensors
    associated with that label.
    """
    client = ctx.find_object(Client)
    label = Label.create(client, attributes={
        'name': name
    })

    ctx.invoke(update, client, label=label.id, **kwargs)


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
@click.option('--add',
              type=ResourceParamType(metavar='SENSOR'),
              help="Add sensors to a label")
@click.option('--remove',
              type=ResourceParamType(metavar='SENSOR'),
              help="Remove sensors from a label")
@click.option('--replace',
              type=ResourceParamType(metavar='SENSOR'),
              help="Replace all sensors in a label")
@click.option('--clear', is_flag=True, default=False,
              help="Remove all sensors from a label")
@click.option('--name',
              help="the new name for the label")
@pass_client
def update(client, label, name, **kwargs):
    """Update sensors in a label.

    Adds, removes, replaces or clears all sensors in the given LABEL.

    """
    label = Label.lookup(client, label)
    if name:
        label.update(attributes={
            'name': name
        })

    all_sensors = Sensor.all(client)
    add_sensors = kwargs.pop('add', None) or []
    remove_sensors = kwargs.pop('remove', None) or []
    clear_sensors = kwargs.pop('clear', False)
    sensors = [Sensor.lookup(client, s, resources=all_sensors)
               for s in add_sensors]
    if sensors:
        label.add_sensors(sensors)

    sensors = [Sensor.lookup(client, s, resources=all_sensors)
               for s in remove_sensors]
    if sensors:
        label.remove_sensors(sensors)

    if clear_sensors:
        label.update_sensors([])

    include = [Sensor]
    label = Label.find(client, label.id, include=include)
    Label.display(client, [label], include=include)

cli.add_command(metadata.cli(Label))
