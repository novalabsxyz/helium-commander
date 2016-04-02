from inspect import getmembers, isfunction
from importlib import import_module
from collections import OrderedDict
import argparse
import tablib
import os
import dpath.util as dpath

__commands__ = ["label", "sensor", "element", "timeseries", "sensor-script"]

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


def register_commands(parser):
    subparsers = parser.add_subparsers(help="one of the helium commands")
    for command_name in __commands__:
        command = import_module(__name__+"."+command_name)
        setup = dict(getmembers(command, isfunction)).get("_register_commands")

        if setup:
            # add the command and sub-commmands
            subparser = subparsers.add_parser(command_name).add_subparsers()
            setup(subparser)

def perform_command(service, opts):
    result = opts.command(service, opts)
    mapping = OrderedDict(opts.mapping) if 'mapping' in opts else None
    if not mapping or not result: return result

    def safe_lookup(o, path):
        try:
            return dpath.get(o, path)
        except KeyError, e:
            return ""

    def map_object(o, mapping):
        return [safe_lookup(o, path) for k, path in mapping.items()]

    mapped_result = [map_object(o, mapping) for o in result]
    data = tablib.Dataset(*mapped_result, headers=mapping.keys())
    return data
