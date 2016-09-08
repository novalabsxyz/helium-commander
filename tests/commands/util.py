from click.testing import CliRunner
from helium_commander.cli import root


def cli_run(args):
    runner = CliRunner()
    result = runner.invoke(root, args)
    assert result.exit_code == 0
    return result.output
