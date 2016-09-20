from helium_commander import Sensor, DataPoint
from itertools import islice
import pytest


def validate_format(output, client, sensors, capsys):
    first_sensor = sensors[0]

    # With sort
    Sensor.display(client, sensors, format=output, sort='name')
    out, err = capsys.readouterr()
    assert first_sensor.short_id in out

    Sensor.display(client, sensors, format=output, sort='name', reverse=True)
    reversed, err = capsys.readouterr()
    assert reversed != out

    # Without sort
    Sensor.display(client, sensors, format=output)
    out, err = capsys.readouterr()
    assert first_sensor.short_id in out

    Sensor.display(client, sensors, format=output, reverse=True)
    reversed, err = capsys.readouterr()
    assert reversed != out


def test_formats(client, sensors, capsys):
    for output in ['csv', 'tabular', 'json']:
        validate_format(output, client, sensors, capsys)

    with pytest.raises(AttributeError):
        Sensor.display(client, sensors, format='xxx')


def test_timeseries(client, authorized_organization):
    points = islice(authorized_organization.timeseries(), 10)
    DataPoint.display(client, points, max_width=20)
