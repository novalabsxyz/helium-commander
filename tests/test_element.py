from __future__ import unicode_literals

from helium_commander import Element, Sensor


def test_display_map(client):
    elements = Element.all(client, include=[Sensor])
    assert len(elements) > 0

    display_map = Element.display_map(client)
    assert display_map is not None

    element = elements[0]
    values = [f(element) for f in display_map.values()]
    assert values is not None
