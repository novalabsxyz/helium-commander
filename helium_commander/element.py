from __future__ import unicode_literals
from helium import Element


def display_map(cls, client):
    def _mac(self):
        return self.meta.mac

    def _count_sensor(self):
        try:
            return len(self.sensors(use_included=True))
        except AttributeError:
            pass
        return None

    def _seen(self):
        try:
            return self.meta.last_seen
        except AttributeError:
            pass
        return None

    def _name(self):
        return getattr(self, 'name', None)

    dict = super(Element, cls).display_map(client)
    dict.update([
        ('mac', _mac),
        ('sensors', _count_sensor),
        ('seen', _seen),
        ('name', _name)
    ])
    return dict

Element.display_map = classmethod(display_map)
