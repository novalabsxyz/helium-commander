from __future__ import unicode_literals
import unicodecsv as csv
import json
import abc
import terminaltables
from textwrap import wrap
from operator import itemgetter


def for_format(format, file, **kwargs):
    json_opts = kwargs.pop('json_opts', None)
    if format == 'json':
        json_opts = json_opts or {
            "indent": 4
        }
        result = JSONWriter(file, json_opts=json_opts, **kwargs)
    elif format == 'csv':
        json_opts = json_opts or {
            "indent": None
        }
        result = CSVWriter(file, json_opts=json_opts, **kwargs)
    elif format == 'tabular':
        json_opts = json_opts or {
            "indent": 0
        }
        result = TabularWriter(file, json_opts=json_opts, **kwargs)

    return result


class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file
        self.json_opts = kwargs.pop('json_opts')

    def start(self, mapping, **kwargs):
        self.sort = kwargs.pop('sort', None)
        self.reverse = kwargs.pop('reverse', False)

    @abc.abstractmethod
    def write_resources(self, resources):
        return

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


class CSVWriter(BaseWriter):

    def start(self, mapping, **kwargs):
        self.writer = csv.DictWriter(file, mapping.keys())
        self.writer.writeheader()

    def write_resources(self, entries, mapping):
        if entries is None:
            return
        for entry in entries:
            row = {key: self.lookup(entry, path)
                   for key, path in mapping.iteritems()}
            self.writer.writerow(row)


class JSONWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(JSONWriter, self).__init__(file, **kwargs)

    def start(self, mapping, **kwargs):
        self.file.write('[\n')
        self.is_first_entries = True

    def write_resources(self, entries, mapping):
        if entries is None:
            return
        for entry in entries:
            if self.is_first_entries:
                self.is_first_entries = False
            else:
                self.file.write(',')

            if mapping:
                entry = {key: self.lookup(entry, path)
                         for key, path in mapping.iteritems()}

            json.dump(entry, self.file, **self.json_opts)

    def finish(self, mapping):
        self.file.write('\n]\n')


class TabularWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(TabularWriter, self).__init__(file, **kwargs)
        self.max_width = kwargs.pop('max_width', None)

    def start(self, mapping, **kwargs):
        super(TabularWriter, self).start(mapping, **kwargs)
        self.data = [[key.upper() for key in mapping.keys()]]

    def order_entries(self, entries, mapping):
        if not mapping:
            return entries
        if self.sort:
            sort_index = mapping.keys().index(self.sort)
            entries = sorted(entries,
                             key=itemgetter(sort_index),
                             reverse=self.reverse)
        elif self.reverse:
            entries = reversed(entries)
        return entries

    def write_resources(self, resources, mapping):
        def map_entry(o):
            return [self.lookup(o, path) for _, path in mapping.items()]

        if resources is None or mapping is None:
            return

        entries = [map_entry(o) for o in resources]
        self.data.extend(self.order_entries(entries, mapping))

    def finish(self, mapping):
        if not hasattr(self, 'data'):
            return

        table = terminaltables.AsciiTable(self.data)
        # table.inner_column_border=False
        # table.inner_heading_row_border=False
        # table.outer_border=False
        last_column = len(mapping) - 1
        max_width = self.max_width or table.column_max_width(last_column)
        for entry in table.table_data:
            entry[last_column] = '\n'.join(wrap(entry[last_column], max_width))
        self.file.write(table.table)
        self.file.write('\n')
