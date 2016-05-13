from collections import OrderedDict
import dpath.util as dpath
import sys
import click
import uuid
import json
import writer
import urlparse


def is_uuid(str):
    try:
        uuid.UUID(str)
        return True
    except ValueError:
        return False

def lookup_resource_id(list, id_rep):
    if hasattr(list, '__call__'):
        list = list().get('data')
    lookup = {}
    _is_uuid = is_uuid(id_rep)
    short_id_matches = []
    name_matches = []
    for entry in list:
        entry_id = entry.get('id')
        if _is_uuid:
            if entry_id == id_rep:
                return entry_id
        else:
            short_id = shorten_id(entry_id)
            if short_id == id_rep:
                short_id_matches.append(entry_id)
            else:
                try:
                    entry_name = dpath.get(entry, "attributes/name")
                    if entry_name == id_rep:
                        name_matches.append(entry_id)
                except KeyError:
                    pass
    if len(short_id_matches) == 0 and len(name_matches) == 0:
        raise KeyError('Id ' + id_rep.encode('ascii')  + ' does not exist')
    elif len(short_id_matches) == 1 and len(name_matches) == 0:
        return short_id_matches[0]
    elif len(short_id_matches) == 0 and len(name_matches) == 1:
        return name_matches[0]
    else:
        raise KeyError('Ambiguous id: ' + id_rep.encode('ascii'))

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
