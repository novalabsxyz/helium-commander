from .util import cli_run


def test_list(client, first_label):
    output = cli_run(['label', 'list'])
    assert first_label.short_id in output

    output = cli_run(['label', 'list', first_label.short_id])
    assert first_label.short_id in output


def test_sensors(client, first_label):
    output = cli_run(['label', 'sensor', first_label.id])
    assert output is not None


def test_create_delete(client, first_sensor):
    output = cli_run(['label', 'create', 'test_label',
                      '--add', first_sensor.short_id])
    assert 'test_label' in output

    output = cli_run(['label', 'sensor', 'test_label'])
    assert first_sensor.short_id in output

    output = cli_run(['label', 'update', 'test_label',
                      '--remove', first_sensor.short_id,
                      '--name', 'renamed_label'])
    assert 'renamed_label' in output

    output = cli_run(['label', 'delete', 'renamed_label'])
    assert output.startswith('Deleted')
