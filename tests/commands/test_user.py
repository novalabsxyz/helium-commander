from .util import cli_run


def test_list(client, authorized_user):
    output = cli_run(client, ['user', 'list'])
    assert authorized_user.short_id in output


def test_update(client, authorized_user):
    name = authorized_user.name
    output = cli_run(client, ['user', 'update',
                              '--name', 'name update'])
    assert 'name update' in output
    output = cli_run(client, ['user', 'update',
                              '--name', name])
