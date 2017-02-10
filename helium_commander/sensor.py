from __future__ import unicode_literals
from helium import Sensor
from operator import attrgetter


def display_map(cls, client, include=None):
    def _meta(attr):
        def func(self):
            return getattr(self.meta, attr, None)
        return func

    dict = super(Sensor, cls).display_map(client, include=include)
    dict.update([
        ('mac', _meta('mac')),
        ('type', _meta('device_type')),
        ('created', _meta('created')),
        ('seen', _meta('last_seen')),
        ('name', attrgetter('name'))
    ])
    return dict

Sensor.display_map = classmethod(display_map)
