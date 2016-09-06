from __future__ import unicode_literals
from helium import User
from operator import attrgetter


def display_map(cls, client):
    dict = super(User, cls).display_map(client)
    dict.update([
        ('name', attrgetter('name')),
    ])
    return dict

User.display_map = classmethod(display_map)
