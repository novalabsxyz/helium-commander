from __future__ import unicode_literals

from helium_commander import User


def test_display_map(client, authorized_user):
    assert authorized_user is not None

    display_map = User.display_map(client)
    assert display_map is not None

    values = [f(authorized_user) for f in display_map.values()]
    assert values is not None
