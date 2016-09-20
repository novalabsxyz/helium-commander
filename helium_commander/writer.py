from __future__ import unicode_literals
import sys
import json
import abc
import terminaltables
from textwrap import wrap
from operator import itemgetter
from future.utils import iteritems
if sys.version_info[0] == 2:    # pragma: no cover
    import unicodecsv as csv
else:                           # pragma: no cover
    import csv


def for_format(format, file):
    json_opts = None
    if format == 'json':
        json_opts = json_opts or {
            "indent": 4
        }
        return JSONWriter(file, json_opts=json_opts)
    elif format == 'csv':
        json_opts = json_opts or {
            "indent": None
        }
        return CSVWriter(file, json_opts=json_opts)
    elif format == 'tabular':
        json_opts = json_opts or {
            "indent": 0
        }
        return TabularWriter(file, json_opts=json_opts)
    else:
        raise AttributeError("Unrecognized format {}".format(format))


class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, json_opts={}):
        self.file = file
        self.json_opts = json_opts

    def start(self, mapping, **kwargs):
        self.sort = kwargs.pop('sort', None)
        self.reverse = kwargs.pop('reverse', False)

    @abc.abstractmethod
    def write_resources(self, resources):
        """Abstract method for subclasses to implement"""

    def finish(self, mapping):
        return

    def lookup(self, o, path):
        result = path(o)
        if result is None:
            return ''
        if isinstance(result, dict) and self.json_opts:
            result = json.dumps(result, **self.json_opts)
        else:
            result = result
        return result

    def order_entries(self, entries, keyfunc):
        if self.sort and keyfunc:
            entries = sorted(entries,
                             key=keyfunc,
                             reverse=self.reverse)
        elif self.reverse:
            entries = reversed(list(entries))
        return entries


class CSVWriter(BaseWriter):

    def start(self, mapping, **kwargs):
        super(CSVWriter, self).start(mapping, **kwargs)
        self.writer = csv.DictWriter(self.file, mapping.keys())
        self.writer.writeheader()

    def write_resources(self, entries, mapping):
        def map_entry(o):
            return {key: self.lookup(o, path)
                    for key, path in iteritems(mapping)}

        entries = map(map_entry, entries)

        keyfunc = itemgetter(self.sort) if self.sort else None
        entries = self.order_entries(entries, keyfunc)
        for entry in entries:
            self.writer.writerow(entry)


class JSONWriter(BaseWriter):

    def start(self, mapping, **kwargs):
        super(JSONWriter, self).start(mapping, **kwargs)
        self.file.write('[\n')
        self.is_first_entries = True

    def write_resources(self, entries, mapping):
        def map_entry(o):
            return {key: self.lookup(o, path)
                    for key, path in iteritems(mapping)}

        entries = map(map_entry, entries)
        keyfunc = itemgetter(self.sort) if self.sort else None
        entries = self.order_entries(entries, keyfunc)

        for entry in entries:
            if self.is_first_entries:
                self.is_first_entries = False
            else:
                self.file.write(',')
            json.dump(entry, self.file, **self.json_opts)

    def finish(self, mapping):
        self.file.write('\n]\n')


class TabularWriter(BaseWriter):

    def start(self, mapping, **kwargs):
        super(TabularWriter, self).start(mapping, **kwargs)
        self.data = [[key.upper() for key in mapping.keys()]]
        self.max_width = kwargs.get('max_width', None)

    def write_resources(self, resources, mapping):
        def map_entry(o):
            return [self.lookup(o, path) for _, path in mapping.items()]

        entries = [map_entry(o) for o in resources]
        if self.sort:
            sort_index = list(mapping.keys()).index(self.sort)
            keyfunc = itemgetter(sort_index)
        else:
            keyfunc = None
        entries = self.order_entries(entries, keyfunc)
        self.data.extend(entries)

    def finish(self, mapping):
        table = terminaltables.AsciiTable(self.data)
        last_column = len(mapping) - 1
        max_width = self.max_width or table.column_max_width(last_column)
        for entry in table.table_data:
            last_field = entry[last_column]
            # check for basic wrap functionality
            if hasattr(last_field, 'expandtabs'):
                entry[last_column] = '\n'.join(wrap(last_field, max_width))
        self.file.write(table.table)
        self.file.write('\n')
