from .util import cli_run
from click.testing import CliRunner
import py.path as path
import pytest


def test_list(client, first_sensor):
    output = cli_run(client, ['sensor', 'list'])
    assert first_sensor.short_id in output

    output = cli_run(client, ['sensor', 'list', first_sensor.short_id])
    assert first_sensor.short_id in output


def test_create_delete(client):
    output = cli_run(client, ['sensor', 'create',
                              '--name', 'test_create_sensor'])
    assert output is not None

    output = cli_run(client, ['sensor', 'update', 'test_create_sensor',
                              '--name', 'updated_name'])

    output = cli_run(client, ['sensor', 'delete', 'updated_name'])
    assert output.startswith('Deleted')


def test_element(client, first_sensor):
    output = cli_run(client, ['sensor', 'element', first_sensor.short_id])
    assert output


def test_label(client, first_sensor):
    output = cli_run(client, ['sensor', 'label', first_sensor.short_id])
    assert output


def test_metadata(client, tmp_sensor):
    output = cli_run(client, ['sensor', 'metadata', 'list',
                              tmp_sensor.short_id])
    assert output is not None

    output = cli_run(client, ['sensor', 'metadata', 'update',
                              tmp_sensor.short_id,
                              '{"test": 42}'])
    assert "42" in output

    output = cli_run(client, ['sensor', 'list',
                              '--metadata', '{"test": 42}'])
    assert tmp_sensor.short_id in output

    output = cli_run(client, ['sensor', 'metadata', 'replace',
                              tmp_sensor.short_id,
                              '{}'])
    assert "42" not in output


def test_timeseries(client, tmp_sensor):
    output = cli_run(client, ['sensor', 'timeseries', 'list',
                              tmp_sensor.short_id])
    assert output is not None

    output = cli_run(client, ['sensor', 'timeseries', 'create',
                              tmp_sensor.short_id, 'test_post', '22'])
    assert '22' in output

    output = cli_run(client, ['sensor', 'timeseries', 'create',
                              tmp_sensor.short_id, 'test_foo', '42'])
    assert '42' in output

    output = cli_run(client, ['sensor', 'timeseries', 'create',
                              tmp_sensor.short_id, 'test_foo', '42',
                              '--timestamp', '2016-05-05T00:00:00Z'])
    assert '2016-05-05' in output


    output = cli_run(client, ['sensor', 'timeseries', 'list',
                              tmp_sensor.short_id,
                              '--port', 'test_post'])
    assert 'test_foo' not in output

    output = cli_run(client, ['sensor', 'timeseries', 'list',
                              tmp_sensor.short_id,
                              '--agg-type', 'min,max',
                              '--agg-size', '5m',
                              '--port', 'test_post'])
    assert 'agg(test_post)' in output
    assert 'agg(min=' in output

    runner = CliRunner()
    with runner.isolated_filesystem():
        file = path.local('test.csv')
        cli_run(client, ['--format', 'csv', '--output', str(file),
                         'sensor', 'timeseries', 'list',
                         tmp_sensor.short_id,
                         '--count', '100'],
                runner=runner)

        output = file.read()
        assert 'test_post' in output
        assert '22' in output
        assert 'test_foo' in output
        assert '42' in output


def test_live(client, tmp_sensor):
    # We're faking the cassette for a live session pretty hard
    # here. The cassette was manually edited to reflect the
    # event/text-stream data in a single request to work around
    # betamax's problems with dealing with live sockets.
    output = cli_run(client, ['--format', 'csv',
                              'sensor', 'timeseries', 'live',
                              tmp_sensor.short_id])
    assert output.count('test_post') == 2

    with pytest.raises(ValueError):
        cli_run(client, ['sensor', 'timeseries', 'live',
                         tmp_sensor.short_id])
