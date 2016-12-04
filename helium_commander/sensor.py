from __future__ import unicode_literals
from helium import Sensor
from operator import attrgetter


def card_type(card_id, default):
    return {
        '2': 'blue',
        '5': 'green',
    }.get(card_id, default)


def display_map(cls, client, include=None):
    def _type(self):
        try:
            card = str(self.meta.card.get('id'))
            return card_type(card, card)
        except AttributeError:
            return None

    def _meta(attr):
        def func(self):
            return getattr(self.meta, attr, None)
        return func

    dict = super(Sensor, cls).display_map(client, include=include)
    dict.update([
        ('mac', _meta('mac')),
        ('type', _type),
        ('created', _meta('created')),
        ('seen', _meta('last_seen')),
        ('name', attrgetter('name'))
    ])
    return dict

Sensor.display_map = classmethod(display_map)
