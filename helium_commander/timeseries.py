from __future__ import unicode_literals
from helium import DataPoint, Timeseries
from operator import attrgetter
from functools import partial


def display_map(func, cls, client, include=None):
    def _sensor(self):
        try:
            sensor_id = self.sensor_id
            return sensor_id.split('-')[0]
        except AttributeError:
            return None

    dict = func(client, include=include)
    dict.update([
        ('sensor', _sensor),
        ('timestamp', attrgetter('timestamp')),
        ('port', attrgetter('port')),
        ('value', attrgetter('value')),
    ])
    return dict

DataPoint.display_map = classmethod(partial(display_map, DataPoint.display_map))
Timeseries                      # Empty reference to make clear we re-export
