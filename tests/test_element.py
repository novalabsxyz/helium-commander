from __future__ import unicode_literals

from helium_commander import Element, Sensor


def test_display_map(client):
    display_map = Element.display_map(client)
    assert display_map is not None

    def validate_display_map(element):
        values = [f(element) for f in display_map.values()]
        assert values is not None

    elements = Element.all(client, include=[Sensor])
    assert len(elements) > 0
    validate_display_map(elements[0])

    elements = Element.all(client)
    assert len(elements) > 0
    validate_display_map(elements[0])
