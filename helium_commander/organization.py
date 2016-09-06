from __future__ import unicode_literals
from helium import Organization
from operator import attrgetter


def display_map(cls, client):
    def _count_user(self):
        return len(self.users(use_included=True))

    def _count_element(self):
        return len(self.elements(use_included=True))

    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    dict = super(Organization, cls).display_map(client)
    dict.update([
        ('users', _count_user),
        ('element', _count_element),
        ('sensor', _count_sensor),
        ('name', attrgetter('name')),
    ])
    return dict

Organization.display_map = classmethod(display_map)
