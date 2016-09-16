import click
import sys
import os
from importlib import import_module
from functools import update_wrapper

from . import __version__
from . import Client


def main_wrapper(cmd, args, **kwargs):
    if args is None:
        args = sys.argv[1:]

    def decorator():
        try:
            cmd.main(args=args, **kwargs)
        except Exception as e:  # pragma: no cover
            if os.environ.get("HELIUM_COMMANDER_DEBUG"):
                raise
            click.secho(str(e), fg='red')
            sys.exit(1)
    return decorator


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


def main_commands(version=None, package=None,  commands=None, name='helium'):
    class Loader(click.MultiCommand):
        def list_commands(self, ctx):
            commands.sort()
            return commands

        def get_command(self, ctx, name):
            try:
                command = import_module(package + "." + name)
                return command.cli
            except ImportError as e:  # pragma: no cover
                click.secho(str(e), fg='red')
                return

    def decorator(f):
        @click.option('--uuid', is_flag=True,
                      help="Whether to display long identifiers")
        @click.option('--format',
                      type=click.Choice(['csv', 'json', 'tabular']),
                      default=None,
                      help="The output format (default 'tabular')")
        @click.option('--output',
                      type=click.File('w'),
                      help="the destination file for results")
        @click.version_option(version=version)
        @click.command(name, cls=Loader, context_settings=CONTEXT_SETTINGS)
        @click.pass_context
        def new_func(ctx, *args, **kwargs):
            ctx.invoke(f, ctx, *args, **kwargs)
        return update_wrapper(new_func, f)
    return decorator


_commands = [
    "user",
    "sensor",
    "element",
    "label",
    "organization",
]


@click.option('--api-key',
              envvar='HELIUM_API_KEY',
              help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable')
@click.option('--host',
              envvar='HELIUM_API_URL',
              default='https://api.helium.com/v1',
              help='The Helium base API URL. Can also be specified using the HELIUM_API_URL environment variable.' )
@main_commands(version=__version__, package='helium_commander.commands', commands=_commands)
def root(ctx, api_key, host, **kwargs):
    ctx.obj = Client(api_token=api_key, base_url=host, **kwargs)


main = main_wrapper(root, None)


if __name__ == '__main__':      # pragma: no cover
    main()
