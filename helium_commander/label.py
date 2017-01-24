from __future__ import unicode_literals
from helium import Label, Sensor, Element
from operator import attrgetter


def display_map(cls, client, include=None):
    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    def _count_element(self):
        return len(self.elements(use_included=True))

    dict = super(Label, cls).display_map(client)
    if include and Sensor in include:
        dict['sensors'] = _count_sensor
    if include and Element in include:
        dict['elements'] = _count_element
    dict.update([
        ('name', attrgetter('name'))
    ])
    return dict

Label.display_map = classmethod(display_map)
