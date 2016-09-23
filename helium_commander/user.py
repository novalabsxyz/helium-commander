from __future__ import unicode_literals
from helium import User
from operator import attrgetter


def display_map(cls, client):
    def _name(self):
        return getattr(self, 'name', None)

    def _email(self):
        """Display the email or the id.

        The public API uses the email as the id. So display that if
        email can not be found for some weird reason.
        """
        return getattr(self, 'email', getattr(self, 'id'))

    dict = super(User, cls).display_map(client, uuid=False)
    dict.update([
        ('email', _email),
        ('name', _name),
    ])
    return dict

User.display_map = classmethod(display_map)
