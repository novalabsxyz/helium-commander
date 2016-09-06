from __future__ import unicode_literals
from helium import Sensor
from operator import attrgetter


def card_type(card_id, default):
    return {
        '2': 'blue',
        '5': 'green',
    }.get(card_id, default)


def display_map(cls, client):
    def _type(self):
        try:
            card = str(self.meta.card.get('id'))
            return card_type(card, card)
        except AttributeError:
            return None

    def _seen(self):
        try:
            return self.meta.last_seen
        except AttributeError:
            pass
        return None

    def _mac(self):
        try:
            return self.meta.mac
        except AttributeError:
            pass
        return None

    dict = super(Sensor, cls).display_map(client)
    dict.update([
        ('mac', _mac),
        ('type', _type),
        ('seen', _seen),
        ('name', attrgetter('name'))
    ])
    return dict

Sensor.display_map = classmethod(display_map)
