from .util import cli_run


def test_list(client, authorized_organization):
    output = cli_run(client, ['organization', 'list'])
    assert authorized_organization.short_id in output


def test_update(client, authorized_organization):
    current_name = authorized_organization.name
    current_tz = authorized_organization.timezone

    output = cli_run(client, ['organization', 'update',
                              '--name', 'test_update_name',
                              '--timezone', 'UTC'])
    assert 'test_update_name' in output
    assert 'UTC' in output

    output = cli_run(client, ['organization', 'update',
                              '--name', current_name,
                              '--timezone', current_tz])
    assert current_name in output
    assert current_tz in output


def test_timeseries(client, authorized_organization):
    output = cli_run(client, ['organization', 'timeseries', 'list'])
    assert output is not None
