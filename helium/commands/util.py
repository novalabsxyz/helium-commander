from collections import OrderedDict
import dpath.util as dpath
import sys
import os
import click
import uuid
import json
import writer
import urlparse
from functools import update_wrapper
from importlib import import_module


def is_uuid(str):
    try:
        uuid.UUID(str)
        return True
    except ValueError:
        return False

def lookup_resource_id(list, id_rep, name_path=None):
    if hasattr(list, '__call__'):
        list = list().get('data')
    _is_uuid = is_uuid(id_rep)
    id_rep_lower = id_rep.lower()
    id_rep_len = len(id_rep)
    name_path = name_path or "attributes/name"
    matches = []
    for entry in list:
        entry_id = entry.get('id')
        if _is_uuid:
            if entry_id == id_rep:
                return entry_id
        else:
            short_id = shorten_id(entry_id)
            if short_id == id_rep:
                matches.append(entry_id.encode('utf8'))
            else:
                try:
                    entry_name = dpath.get(entry, name_path)
                    if entry_name[:id_rep_len].lower() == id_rep_lower:
                        matches.append(entry_id.encode('utf8'))
                except KeyError:
                    pass
    if len(matches) == 0:
        raise KeyError('Id: ' + id_rep.encode('utf8')  + ' does not exist')
    elif len(matches) > 1:
        short_matches = [shorten_id(id) for id in matches]
        raise KeyError('Ambiguous id: ' + id_rep.encode('utf8') + ' (' + ', '.join(short_matches) + ')')

    return matches[0]


def shorten_id(str):
    return str.split('-')[0]

def shorten_json_id(json):
    # Ugh, reaching for global state isn't great but very convenient here
    try:
        shorten = not click.get_current_context().find_root().params.get('uuid', False)
    except:
        shorten = False
    json_id = json.get('id')
    return shorten_id(json_id) if shorten else json_id


def tabulate(result, map):
    mapping = OrderedDict(map)
    if not mapping or not result: return result

    # Ugh, reaching for global state isn't great but very convenient here
    default_format = 'tty' if sys.stdout.isatty() else 'csv'
    format = click.get_current_context().find_root().params.get('format')
    # Ensure format is set to something sensible
    format = format or default_format
    file = click.utils.get_text_stream('stdout')
    output = writer.for_format(format, file, mapping=mapping)
    output.start()
    output.write_entries(result)
    output.finish()

def map_script_filenames(json):
    files = dpath.get(json, 'meta/scripts')
    return ', '.join(extract_script_filenames(files))

def extract_script_filenames(files):
    return [urlparse.urlsplit(url).path.split('/')[-1] for url in files]

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)



def cli(version=None, package=None,  commands=None):
    class Loader(click.MultiCommand):
        def list_commands(self, ctx):
            commands.sort()
            return commands
        def get_command(self, ctx, name):
            try:
                command = import_module(package +"."+name)
                return command.cli
            except ImportError, e:
                click.secho(str(e), fg='red')
                return

    def decorator(f):
        @click.option('--uuid', is_flag=True,
                      help="Whether to display long identifiers")
        @click.option('--format', type=click.Choice(['csv', 'json', 'tty']), default=None,
                      help="The output format (default 'tty')")
        @click.version_option(version=version)
        @click.command(cls=Loader, context_settings=CONTEXT_SETTINGS)
        @click.pass_context
        def new_func(ctx, *args, **kwargs):
            ctx.invoke(f, ctx, *args, **kwargs)
        return update_wrapper(new_func, f)
    return decorator


def main(cli):
    def decorator():
        args = sys.argv[1:]
        try:
            cli.main(args=args, prog_name=None)
        except Exception, e:
            if os.environ.get("HELIUM_COMMANDER_DEBUG"):
                raise
            click.secho(str(e), fg='red')
            sys.exit(1)
    return decorator
