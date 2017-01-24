from .util import cli_run


def test_list(client, first_label):
    output = cli_run(client, ['label', 'list'])
    assert first_label.short_id in output

    output = cli_run(client, ['label', 'list', first_label.short_id])
    assert first_label.short_id in output


def test_sensors(client, tmp_label, tmp_sensor):
    output = cli_run(client, ['label', 'sensor', tmp_label.id])
    assert output is not None

    output = cli_run(client, ['label', 'sensor', tmp_label.id,
                              '--add', tmp_sensor.short_id])
    assert tmp_sensor.short_id in output

    output = cli_run(client, ['label', 'sensor', tmp_label.id,
                              '--remove', tmp_sensor.short_id])
    assert tmp_sensor.short_id not in output

    output = cli_run(client, ['label', 'sensor', tmp_label.id,
                              '--replace', tmp_sensor.short_id])
    assert tmp_sensor.short_id in output

    output = cli_run(client, ['label', 'sensor', tmp_label.id,
                              '--replace', 'none'])
    assert tmp_sensor.short_id not in output


def test_elements(client, tmp_label, first_element):
    output = cli_run(client, ['label', 'element', tmp_label.id])
    assert output is not None

    output = cli_run(client, ['label', 'element', tmp_label.id,
                              '--add', first_element.short_id])
    assert first_element.short_id in output

    output = cli_run(client, ['label', 'element', tmp_label.id,
                              '--remove', first_element.short_id])
    assert first_element.short_id not in output

    output = cli_run(client, ['label', 'element', tmp_label.id,
                              '--replace', first_element.short_id])
    assert first_element.short_id in output

    output = cli_run(client, ['label', 'element', tmp_label.id,
                              '--replace', 'none'])
    assert first_element.short_id not in output


def test_create_delete(client, first_sensor, first_element):
    output = cli_run(client, ['label', 'create', 'test_label',
                              '--sensors', first_sensor.short_id,
                              '--elements', first_element.short_id])
    assert 'test_label' in output

    output = cli_run(client, ['label', 'update',
                              'test_label',
                              '--name', 'renamed_label'])
    assert 'renamed_label' in output

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
                              tmp_label.short_id,
                              '{}'])
    assert "42" not in output
