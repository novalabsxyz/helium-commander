from .util import cli_run


def test_list(client, authorized_organization):
    output = cli_run(client, ['organization', 'list'])
    assert authorized_organization.short_id in output


def test_update(client, authorized_organization):
    current_name = authorized_organization.name

    output = cli_run(client, ['organization', 'update',
                      '--name', 'test_update_name'])
    assert 'test_update_name' in output

    output = cli_run(client, ['organization', 'update',
                      '--name', current_name])
    assert current_name in output
