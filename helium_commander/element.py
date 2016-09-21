from __future__ import unicode_literals
from helium import Element
from operator import attrgetter


def display_map(cls, client):
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

    dict = super(Element, cls).display_map(client)
    dict.update([
        ('mac', _mac),
        ('sensors', _count_sensor),
        ('seen', _seen),
        ('name', attrgetter('name')),
    ])
    return dict

Element.display_map = classmethod(display_map)
