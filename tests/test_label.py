from __future__ import unicode_literals

from helium_commander import Label, Sensor


def test_display_map(client, capsys):
    labels = Label.all(client, include=[Sensor])
    assert len(labels) > 0

    display_map = Label.display_map(client)
    assert display_map is not None

    label = labels[0]
    values = [f(label) for f in display_map.values()]
    assert values is not None

    Label.display(client, [label])
    out, err = capsys.readouterr()
    assert label.short_id in out
