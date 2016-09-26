from __future__ import unicode_literals
from helium import User
from helium import response_json


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


def authenticate(cls, client, email, password):   # pragma: no cover
    url = client._build_url('user', 'auth')
    json = {
        'email': email,
        'password': password
    }
    json = response_json(client.post(url, json=json), 200, extract=None)
    return cls._mk_one(client, json)

User.display_map = classmethod(display_map)
User.authenticate = classmethod(authenticate)
