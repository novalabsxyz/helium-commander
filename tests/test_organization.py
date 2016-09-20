from __future__ import unicode_literals

from helium_commander import Organization, Sensor, Element, User


def test_display_map(client):
    org = Organization.singleton(client, include=[Sensor, Element, User])
    assert org is not None

    display_map = Organization.display_map(client)
    assert display_map is not None

    values = [f(org) for f in display_map.values()]
    assert values is not None
