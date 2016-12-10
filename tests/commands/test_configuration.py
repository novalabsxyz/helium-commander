from .util import cli_run
from helium_commander import Configuration


def test_list(client, first_configuration):
    output = cli_run(client, ['configuration', 'list'])
    assert first_configuration.short_id in output

    output = cli_run(client, ['configuration', 'list',
                              first_configuration.short_id])
    assert first_configuration.short_id in output


def test_create_delete(client):
    test_id = "test.configuration.create_delete"
    output = cli_run(client, ['configuration', 'create',
                              '{{ "test_id": "{}" }}'.format(test_id)])
    assert output is not None
    assert test_id in output

    configs = Configuration.all(client)
    for config in configs:
        if getattr(config, 'test_id', None) == test_id:
            output = cli_run(client, ['configuration', 'delete',
                                      config.short_id])
            assert output.startswith('Deleted')


def test_device(client, first_configuration):
    output = cli_run(client, ['configuration', 'device',
                              first_configuration.short_id])
    assert output


def test_update(client, tmp_configuration, first_sensor):
    output = cli_run(client, ['configuration', 'update',
                              tmp_configuration.short_id])
    assert tmp_configuration.short_id not in output

    output = cli_run(client, ['configuration', 'update',
                              tmp_configuration.short_id,
                              '--add', first_sensor.short_id])
    assert first_sensor.short_id in output

    output = cli_run(client, ['configuration', 'update',
                              tmp_configuration.short_id,
                              '--remove', first_sensor.short_id])
    assert first_sensor.short_id not in output
