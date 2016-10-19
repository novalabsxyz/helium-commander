from __future__ import unicode_literals
from helium import Organization, User, Element, Sensor
from operator import attrgetter


def display_map(cls, client, include=None):
    def on_include(dict, cls, name, func):
        if include and cls in include:
            dict[name] = func

    def _count_user(self):
        return len(self.users(use_included=True))

    def _count_element(self):
        return len(self.elements(use_included=True))

    def _count_sensor(self):
        return len(self.sensors(use_included=True))

    dict = super(Organization, cls).display_map(client)

    on_include(dict, User, 'users', _count_user)
    on_include(dict, Element, 'elements', _count_element)
    on_include(dict, Sensor, 'sensors', _count_sensor)
    dict['name'] = attrgetter('name')
    return dict

Organization.display_map = classmethod(display_map)
