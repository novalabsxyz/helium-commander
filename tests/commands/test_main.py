import pytest
from click import UsageError
from helium_commander.cli import root, _commands, main_wrapper
from .util import cli_run


def main_run(args):
    try:
        main_wrapper(root, args,
                     standalone_mode=False)()
    except SystemExit:
        pass


def test_main(capsys):
    main_run(['--help'])
    out, err = capsys.readouterr()
    assert len(err) == 0
    for cmd in _commands:
        main_run([cmd, '--help'])
        assert len(err) == 0
        assert len(out) > 0


def test_unknown_command(client):
    with pytest.raises(UsageError):
        cli_run(client, ['foo', '--help'])
