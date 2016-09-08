import click
from click.testing import CliRunner
from helium_commander.options import (
    device_sort_option,
    device_mac_option
)


def cli_run(func, args, output):
    runner = CliRunner()
    result = runner.invoke(func, args)
    assert result.exit_code == 0
    assert result.output == output


def test_sort():

    @click.command()
    @device_sort_option
    def func(reverse, sort):
        click.echo('{} {}'.format(sort, reverse))

    cli_run(func, ['--sort', 'name', '--reverse'],
            '{} {}\n'.format('name', 'True'))
    cli_run(func, ['--sort', 'seen'],
            '{} {}\n'.format('seen', 'False'))
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
