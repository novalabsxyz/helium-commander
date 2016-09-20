from __future__ import unicode_literals
from helium import Label
from operator import attrgetter


def display_map(cls, client):
    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    dict = super(Label, cls).display_map(client)
    dict.update([
        ('sensors', _count_sensor),
        ('name', attrgetter('name')),
    ])
    return dict

Label.display_map = classmethod(display_map)
