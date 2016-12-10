"""Configuration commands."""
import click
from builtins import filter
from helium_commander import (
    Sensor,
    Element,
    Client,
    Configuration,
    Device,
    DeviceConfiguration,
    JSONParamType,
    ResourceParamType,
    device_mac_option
)

pass_client = click.make_pass_decorator(Client)


@click.group()
def cli():
    """Operations on configurations."""
    pass


@cli.command()
@click.argument('config', required=False)
@pass_client
def list(client, config):
    """List configurations.

    Lists one CONFIGuration or all configurations associated with the
    authorized organization.

    """
    include = [DeviceConfiguration]
    if config:
        configs = [Configuration.lookup(client, config, include=include)]
    else:
        configs = Configuration.all(client, include=include)
    Configuration.display(client, configs, include=include)


@cli.command()
@click.argument('value', type=JSONParamType())
@pass_client
def create(client, value):
    """Create a configuration.

    Create a configuration with a given set of JSON attributes.

    """
    config = Configuration.create(client, attributes=value)
    Configuration.display(client, [config])


@cli.command()
@click.argument('config')
@pass_client
def delete(client, config):
    """Delete a configuration.

    Deletes a given CONFIGuration. This will fail if there are already
    are devices targetted for a given configuration.

    """
    config = Configuration.lookup(client, config)
    config.delete()
    click.echo('Deleted {}'.format(config.id))


_dev_config_includes = [Device, Configuration]

def _dev_configs(client, config):
    include = _dev_config_includes
    dev_configs = DeviceConfiguration.all(client, include=include)
    return filter(lambda dc:
                  dc.configuration(use_included=True) == config,
                  dev_configs)




@cli.command()
@click.argument('config')
@pass_client
def device(client, config):
    """List associated device configurations.

    A configuration can be applied to zero or more devices through
    "device configurations".

    This lists all the device configurations associated with the given
    CONFIGuration.

    Note: The id of the listed device configuration is NOT the id of
    the device the configuration is applied to. Look for the DEVICE
    column to see the actual targeted device ids.

    """
    config = Configuration.lookup(client, config)

    dev_configs = _dev_configs(client, config)
    DeviceConfiguration.display(client, dev_configs,
                                include=_dev_config_includes)


@cli.command()
@click.argument('config')
@click.option('--add', type=ResourceParamType(metavar='DEVICE'),
              help="Add devices to a configuration")
@click.option('--remove', type=ResourceParamType(metavar='DEVICE'),
              help="Remove devices from a configuration")
@click.option('--type',
              type=click.Choice(['sensor', 'element']),
              default='sensor',
              help="The type of device to add or remove (default sensor).")
@device_mac_option
@pass_client
def update(client, config, add, remove, type, mac):
    """Updates the devices for a configuration.

    Applies or removes a configuration from one or more given DEVICES.

    The type of the DEVICES to apply the configuration to defaults to
    sensors but can be overridden for the given list of devices using
    the --type option.

    DEVICES can be specified using a comma separated list of either
    short or long resource ids, or in a file using "@filename". The
    file should contain newline separated short or long resource ids.

    Note: A device can only have at most one loaded and one unloaded
    (or pending) configuration associated with it. When you apply a
    configuraiton to a device it is always in unloaded state. Loading
    a configuration does NOT happen immediately and can take some time
    depending on how often the device communicates with the helium
    system.

    If you apply multiple configurations to a device the last one
    wins.

    Note: When you remove a configuration that was already "loaded"
    for a given device, removing that configuration has NO effect
    since the system has already processed that configuration for the
    device.

    """
    config = Configuration.lookup(client, config)
    clazz = {
        'sensor': Sensor,
        'element': Element
    }
    add_devices = add or []
    remove_devices = remove or []
    all_devices = clazz[type].all(client)

    # Process adds
    devices = [clazz[type].lookup(client, d, mac=mac, resources=all_devices)
               for d in add_devices]
    if devices:
        map(lambda d: DeviceConfiguration.create(client,
                                                 device=d,
                                                 configuration=config),
            devices)

    # Process removes
    devices = [clazz[type].lookup(client, d, mac=mac, resources=all_devices)
               for d in remove_devices]
    if devices:
        dev_configs = _dev_configs(client, config)
        devices = frozenset(devices)
        dev_configs = filter(lambda dc:
                             dc.device(use_included=True) in devices,
                             dev_configs)
        map(lambda dc: dc.delete(), dev_configs)

    # Re-fetch to include full device information
    dev_configs = _dev_configs(client, config)
    DeviceConfiguration.display(client, dev_configs,
                                include=_dev_config_includes)
