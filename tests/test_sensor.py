from __future__ import unicode_literals

from helium_commander import Sensor
from helium_commander import resource
import pytest


def test_lookup(client, sensors, first_sensor):
    assert len(sensors) > 0
    # Look up by id
    lookup_sensor = Sensor.lookup(client, first_sensor.id,
                                  resources=sensors)
    assert first_sensor == lookup_sensor
    # Look up by short_id
    lookup_sensor = Sensor.lookup(client, first_sensor.short_id,
                                  resources=sensors)
    assert first_sensor == lookup_sensor
    # Look up by mac
    assert first_sensor.meta.last_seen is not None
    assert first_sensor.meta.mac is not None
    lookup_sensor = Sensor.lookup(client, first_sensor.meta.mac, mac=True,
                                  resources=sensors)
    assert first_sensor == lookup_sensor
    # Lookup by name
    lookup_sensor = Sensor.lookup(client, first_sensor.name,
                                  resources=sensors)
    assert first_sensor == lookup_sensor
    lookup_sensor = Sensor.filter(client, None,
                                  resource.filter_string_attribute('name'),
                                  resources=sensors)
    assert len(lookup_sensor) > 0

    # Test some lookup failures
    with pytest.raises(KeyError):
        Sensor.lookup(client, '8', mac=True)
    with pytest.raises(KeyError):
        Sensor.lookup(client, 'zzfs', mac=True)


def test_display_map(client, first_sensor, sensors):
    assert first_sensor is not None

    display_map = Sensor.display_map(client)
    assert display_map is not None

    for sensor in sensors:
        values = [f(sensor) for f in display_map.values()]
        assert values is not None
