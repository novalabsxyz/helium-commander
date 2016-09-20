from __future__ import unicode_literals

from helium_commander import DataPoint
from itertools import islice


def test_display_map(client, first_sensor):
    assert first_sensor is not None

    display_map = DataPoint.display_map(client)
    assert display_map is not None

    readings = islice(first_sensor.timeseries(), 5)
    for reading in readings:
        values = [f(reading) for f in display_map.values()]
        assert values is not None
