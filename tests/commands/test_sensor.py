from .util import cli_run


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
