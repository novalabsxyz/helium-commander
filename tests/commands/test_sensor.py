from helium_commander.cli import root
from click.testing import CliRunner


def cli_run(args):
    runner = CliRunner()
    result = runner.invoke(root, args)
    assert result.exit_code == 0
    return result.output


def test_list(client, first_sensor):
    output = cli_run(['sensor', 'list'])
    assert first_sensor.short_id in output

    output = cli_run(['sensor', 'list', first_sensor.short_id])
    assert first_sensor.short_id in output


def test_create_delete(client):
    output = cli_run(['sensor', 'create',
                      '--name', 'test_create_sensor'])
    assert output is not None

    output = cli_run(['sensor', 'update', 'test_create_sensor',
                      '--name', 'updated_name'])

    output = cli_run(['sensor', 'delete', 'updated_name'])
    assert output.startswith('Deleted')
