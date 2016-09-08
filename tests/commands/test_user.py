from .util import cli_run


def test_list(client, authorized_user):
    output = cli_run(['user', 'list'])
    assert authorized_user.short_id in output
