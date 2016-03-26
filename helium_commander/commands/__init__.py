from inspect import getmembers, isfunction
from importlib import import_module
import argparse
import tablib
import os
import dpath.util as dpath

__commands__ = ["label", "sensor", "element"]

class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def _mk_action(action, mapping=None):
    class commandAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            setattr(args, self.dest, values)
            setattr(args, "command", action)
            setattr(args, "mapping", mapping)
    return commandAction


def register_commands(parser):
    subparsers = parser.add_subparsers(help="one of the helium commands")
    for command_name in __commands__:
        command = import_module(__name__+"."+command_name)
        setup = dict(getmembers(command, isfunction)).get("_register_commands")

        if setup:
            # add the command and sub-commmands
            subparser = subparsers.add_parser(command_name).add_subparsers()
            setup(subparser, _mk_action)

def perform_command(service, opts):
    result = opts.command(service, opts)
    mapping = opts.mapping
    if not mapping or not result: return result

    def map_object(o, mapping):
        return [dpath.get(o, path) for k, path in mapping.items()]

    mapped_result = [map_object(o, mapping) for o in result]
    data = tablib.Dataset(*mapped_result, headers=mapping.keys())
    return data
