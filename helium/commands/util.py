from collections import OrderedDict
import dpath.util as dpath
import tablib
import sys
import click

def tabulate(result, map):
    mapping = OrderedDict(map)
    if not mapping or not result: return result

    def _lookup(o, path):
        try:
            if hasattr(path, '__call__'):
                return path(o)
            else:
                return dpath.get(o, path)
        except KeyError, e:
            return ""

    def map_object(o, mapping):
        return [_lookup(o, path) for k, path in mapping.items()]

    mapped_result = [map_object(o, mapping) for o in result]
    data = tablib.Dataset(*mapped_result, headers=mapping.keys())
    return data

def output(result):
    if sys.stdout.isatty():
        click.echo(result)
    elif result.export:
        click.echo(result.export('csv'))
    else:
        click.echo(result)
