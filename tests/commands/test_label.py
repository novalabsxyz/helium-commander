from .util import cli_run


def test_list(client, first_label):
    output = cli_run(client, ['label', 'list'])
    assert first_label.short_id in output

    output = cli_run(client, ['label', 'list', first_label.short_id])
    assert first_label.short_id in output


def test_sensors(client, first_label):
    output = cli_run(client, ['label', 'sensor', first_label.id])
    assert output is not None


def test_create_delete(client, first_sensor):
    output = cli_run(client, ['label', 'create', 'test_label',
                              '--add', first_sensor.short_id])
    assert 'test_label' in output

    output = cli_run(client, ['label', 'sensor', 'test_label'])
    assert first_sensor.short_id in output

    output = cli_run(client, ['label', 'update',
                              'test_label',
                              '--remove', first_sensor.short_id,
                              '--name', 'renamed_label'])
    assert 'renamed_label' in output

    output = cli_run(client, ['label', 'update',
                              'renamed_label',
                              '--replace', first_sensor.short_id])
    assert 'renamed_label' in output

    output = cli_run(client, ['label', 'update',
                              'renamed_label',
                              '--clear'])
    assert output

    output = cli_run(client, ['label', 'delete', 'renamed_label'])
    assert output.startswith('Deleted')


def test_metadata(client, tmp_label):
    output = cli_run(client, ['label', 'metadata', 'list',
                              tmp_label.short_id])
    assert output is not None

    output = cli_run(client, ['label', 'metadata', 'update',
                              tmp_label.short_id,
                              '{"test": 42}'])
    assert "42" in output

    output = cli_run(client, ['label', 'list',
                              '--metadata', '{"test": 42}'])
    assert tmp_label.short_id in output

    output = cli_run(client, ['label', 'metadata', 'replace',
                              label_sensor.short_id,
                              '{}'])
    assert "42" not in output
