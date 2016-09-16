from click.testing import CliRunner
from helium_commander.cli import main_commands, _commands, __version__


def cli_run(client, args, runner=None):
    @main_commands(version=__version__,
                   package='helium_commander.commands',
                   commands=_commands)
    def root_runner(ctx, **kwargs):
        # Since we need to use the betamax wrapped client, we inject
        # known global command line options into the curent client
        client.uuid = kwargs.get('uuid', None) or False
        client.format = kwargs.get('format', None) or 'tabular'
        client.output = kwargs.get('output', None)
        ctx.obj = client

    runner = runner or CliRunner()
    result = runner.invoke(root_runner, args,
                           catch_exceptions=False,
                           standalone_mode=False)
    assert result.exit_code == 0
    return result.output
