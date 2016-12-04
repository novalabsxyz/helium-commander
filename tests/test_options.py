import click
from click.testing import CliRunner
from click import BadParameter
import json
from helium_commander.options import (
    device_sort_option,
    device_mac_option,
    ResourceParamType,
    JSONParamType
)
import pytest


def cli_run(func, args, output):
    runner = CliRunner()
    result = runner.invoke(func, args,
                           catch_exceptions=False,
                           standalone_mode=False)
    assert result.exit_code == 0
    if output is not None:
        assert result.output == output
    return result.output


def test_sort():

    @click.command()
    @device_sort_option
    def func(reverse, sort):
        click.echo('{} {}'.format(sort, reverse))

    cli_run(func, ['--sort', 'name', '--reverse'],
            '{} {}\n'.format('name', 'True'))
    cli_run(func, ['--sort', 'seen'],
            '{} {}\n'.format('seen', 'False'))
    cli_run(func, ['--sort', 'created'],
            '{} {}\n'.format('created', 'False'))
    cli_run(func, ['--reverse'],
            '{} {}\n'.format('None', 'True'))


def test_mac():
    @click.command()
    @device_mac_option
    def func(mac):
        click.echo('{}'.format(mac))

    cli_run(func, ['--mac'],
            '{}\n'.format('True'))
    cli_run(func, None,
            '{}\n'.format('False'))


def test_resource(tmpdir):
    @click.command()
    @click.option('--add',
                  type=ResourceParamType(metavar='SENSOR'))
    def func(add):
        click.echo(','.join(add))

    output = cli_run(func, ['--help'], None)
    assert '--add SENSOR[,SENSOR,...]* | @filename' in output

    output = cli_run(func, ['--add', '234,567'],
                     '234,567\n')

    file = tmpdir.join('ids.txt')
    file.write('123\n456\n')
    output = cli_run(func, ['--add', '@{}'.format(file)],
                     '123,456\n')


def test_json():
    @click.command()
    @click.argument('value', type=JSONParamType())
    def func(value):
        click.echo(json.dumps(value))

    cli_run(func, ['42'], '42\n')

    with pytest.raises(BadParameter):
        cli_run(func, ['abc'], 'abc')
