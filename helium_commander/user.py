from __future__ import unicode_literals
from helium import CB, User


def display_map(cls, client, include=None):
    def _name(self):
        return getattr(self, 'name', None)

    def _email(self):
        """Display the email or the id.

        The public API uses the email as the id. So display that if
        email can not be found for some weird reason.
        """
        return getattr(self, 'email', getattr(self, 'id'))

    def _pending(self):
        return 'yes' if self.meta.pending_invite else 'no'

    dict = super(User, cls).display_map(client, uuid=False, include=include)
    dict.update([
        ('email', _email),
        ('pending', _pending),
        ('name', _name),
    ])
    return dict


def authenticate(cls, client, email, password):   # pragma: no cover
    url = client._build_url('user', 'auth')
    json = {
        'email': email,
        'password': password
    }
    process = cls._mk_one(client)
    return client.post(url, CB.json(200, process), json=json)

User.display_map = classmethod(display_map)
User.authenticate = classmethod(authenticate)
