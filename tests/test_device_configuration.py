from __future__ import unicode_literals

from helium_commander import DeviceConfiguration, Device, Configuration


def test_display_map(client):
    include = [Device, Configuration]
    dev_configs = DeviceConfiguration.all(client, include=include)
    assert len(dev_configs) > 0

    display_map = DeviceConfiguration.display_map(client, include=include)
    assert display_map is not None

    for config in dev_configs:
        values = [f(config) for f in display_map.values()]
        assert values is not None
