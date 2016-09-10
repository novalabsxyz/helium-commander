from .util import cli_run


def test_list(client, first_element):
    output = cli_run(client, ['element', 'list'])
    assert first_element.short_id in output

    output = cli_run(client, ['element', 'list', first_element.short_id])
    assert first_element.short_id in output


def test_update(client, first_element):
    current_name = first_element.name
    output = cli_run(client, ['element', 'update', first_element.short_id,
                      '--name', 'test_update_name'])
    assert 'test_update_name' in output

    output = cli_run(client, ['element', 'update', first_element.short_id,
                      '--name', current_name])
    assert current_name in output
