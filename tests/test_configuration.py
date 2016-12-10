from __future__ import unicode_literals

from helium_commander import Configuration, DeviceConfiguration


def test_display_map(client):
    include = [DeviceConfiguration]
    configs = Configuration.all(client, include=include)
    assert len(configs) > 0

    display_map = Configuration.display_map(client, include=include)
    assert display_map is not None

    for config in configs:
        values = [f(config) for f in display_map.values()]
        assert values is not None
