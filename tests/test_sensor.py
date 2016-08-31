from __future__ import unicode_literals

from helium_commander import Sensor
import pytest


def test_lookup(client, sensors):
    assert len(sensors) > 0

    sensor = sensors[0]

    lookup_sensor = Sensor.lookup(client, sensor.id, resources=sensors)
    assert sensor == lookup_sensor

    lookup_sensor = Sensor.lookup(client, sensor.short_id)
    assert sensor == lookup_sensor

    assert sensor.meta.mac is not None
    lookup_sensor = Sensor.lookup(client, sensor.meta.mac, mac=True)
    assert sensor == lookup_sensor

    with pytest.raises(KeyError):
        Sensor.lookup(client, 'zzfs', mac=True)

    with pytest.raises(KeyError):
        Sensor.lookup(client, '8', mac=True)
