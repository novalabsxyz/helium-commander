from __future__ import unicode_literals
from helium import Element, Sensor


def display_map(cls, client, include=None):
    def _mac(self):
        return self.meta.mac

    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    def _seen(self):
        try:
            return self.meta.last_seen
        except AttributeError:
            pass
        return None

    def _name(self):
        return getattr(self, 'name', None)

    dict = super(Element, cls).display_map(client, include=include)
    dict.update([
        ('mac', _mac)
    ])

    if include and Sensor in include:
        dict['sensors'] = _count_sensor

    dict.update([
        ('seen', _seen),
        ('name', _name)
    ])
    return dict

Element.display_map = classmethod(display_map)
