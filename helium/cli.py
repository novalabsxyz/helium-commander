import helium
import click
from . import commands
from .version import __version__

_commands = [
    "label",
    "sensor",
    "element",
    "sensor-script",
    "cloud-script",
    "organization",
    "user"
]

@click.option('--api-key',
              envvar='HELIUM_API_KEY',
              help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable')
@click.option('--host',
              envvar='HELIUM_API_URL',
              default=None,
              help= 'The Helium base API URL. Can also be specified using the HELIUM_API_URL environment variable.' )
@commands.cli(version=__version__, package='helium.commands', commands = _commands)
def cli(ctx, api_key, host, **kwargs):
    ctx.obj = helium.Service(api_key, host)

main = commands.main(cli)

if __name__ == '__main__':
    main()
