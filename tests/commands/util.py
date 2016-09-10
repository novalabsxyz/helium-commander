from click.testing import CliRunner
from helium_commander.cli import main_commands, _commands, __version__


def cli_run(client, args):
    @main_commands(version=__version__, package='helium_commander.commands',
                   commands=_commands)
    def root_runner(ctx, **kwargs):
        ctx.obj = client

    runner = CliRunner()
    result = runner.invoke(root_runner, args,
                           catch_exceptions=False,
                           standalone_mode=False)
    assert result.exit_code == 0
    return result.output
