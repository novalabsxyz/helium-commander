from __future__ import unicode_literals
from helium import Element, Sensor


def display_map(cls, client, include=None):
    def _mac(self):
        return self.meta.mac

    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    def _seen(self):
        return getattr(self.meta, 'last_seen', None)

    def _connected(self):
        state = getattr(self.meta, 'connected', None)
        return 'yes' if state is True else 'no'

    def _name(self):
        return getattr(self, 'name', None)

    dict = super(Element, cls).display_map(client, include=include)
    dict.update([
        ('mac', _mac)
    ])

    if include and Sensor in include:
        dict['sensors'] = _count_sensor

    dict.update([
        ('connected', _connected),
        ('seen', _seen),
        ('name', _name)
    ])
    return dict

Element.display_map = classmethod(display_map)
