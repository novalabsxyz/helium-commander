import unicodecsv as csv
import json
import abc
import terminaltables
import dpath.util as dpath
from textwrap import wrap
from operator import itemgetter
from collections import OrderedDict
from contextlib import contextmanager


@contextmanager
def for_format(format, file, **kwargs):
    json_opts = kwargs.pop('json', None)
    if format == 'json':
        json_opts = json_opts or {
            "indent": 4
        }
        result = JSONWriter(file, json=json_opts, **kwargs)
    elif format == 'csv':
        json_opts = json_opts or {
            "indent": None
        }
        result = CSVWriter(file, json=json_opts, **kwargs)
    elif format == 'tabular':
        json_opts = json_opts or {
            "indent": 0
        }
        result = TerminalWriter(file, json=json_opts, **kwargs)
    try:
        result.start()
        yield result
    finally:
        result.finish()


class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file
        self.mapping = OrderedDict(kwargs.pop('mapping'))
        self.json_opts = kwargs.pop('json', None)
        self.sort = kwargs.pop('sort', None)
        self.reverse = kwargs.pop('reverse', False)

    def start(self):
        return

    @abc.abstractmethod
    def write_entries(self, entries):
        return

    def finish(self):
        return

    def lookup(self, o, path, **kwargs):
        try:
            if hasattr(path, '__call__'):
                result = path(o)
            else:
                result = dpath.get(o, path)
        except KeyError:
            return ""
        json_opts = kwargs.pop('json', None)
        if isinstance(result, dict) and json_opts:
            result = json.dumps(result, **json_opts)
        else:
            result = result
        return result


class CSVWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(CSVWriter, self).__init__(file, **kwargs)
        self.writer = csv.DictWriter(file, self.mapping.keys())

    def start(self):
        self.writer.writeheader()

    def write_entries(self, entries):
        if entries is None:
            return
        for entry in entries:
            row = {key: self.lookup(entry, path, json=self.json_opts)
                   for key, path in self.mapping.iteritems()}
            self.writer.writerow(row)


class JSONWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(JSONWriter, self).__init__(file, **kwargs)

    def start(self):
        self.file.write('[\n')
        self.is_first_entries = True

    def write_entries(self, entries):
        if entries is None:
            return
        for entry in entries:
            if self.is_first_entries:
                self.is_first_entries = False
            else:
                self.file.write(',')

            if self.mapping:
                entry = {key: self.lookup(entry, path)
                         for key, path in self.mapping.iteritems()}

            json.dump(entry, self.file, **self.json_opts)

    def finish(self):
        self.file.write('\n]\n')


class TerminalWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(TerminalWriter, self).__init__(file, **kwargs)
        self.data = [[key.upper() for key in self.mapping.keys()]]
        self.json_opts = kwargs.pop('json', None)
        self.max_width = kwargs.pop('max_width', None)

    def start(self):
        pass

    def order_entries(self, entries):
        if not self.mapping:
            return entries
        if self.sort:
            sort_index = self.mapping.keys().index(self.sort)
            entries = sorted(entries,
                             key=itemgetter(sort_index),
                             reverse=self.reverse)
        elif self.reverse:
            entries = reversed(entries)
        return entries

    def write_entries(self, entries):
        def safe_unicode(o, *args):
            try:
                return unicode(o, *args)
            except UnicodeDecodeError:
                return unicode(str(o).encode('string_escape'))

        def map_entry(o):
            return [safe_unicode(self.lookup(o, path, json=self.json_opts))
                    for _, path in self.mapping.items()]

        if entries is None:
            return
        if self.mapping:
            entries = [map_entry(o) for o in entries]

        self.data.extend(self.order_entries(entries))

    def finish(self):
        table = terminaltables.AsciiTable(self.data)
        # table.inner_column_border=False
        # table.inner_heading_row_border=False
        # table.outer_border=False
        last_column = len(self.mapping) - 1
        max_width = self.max_width or table.column_max_width(last_column)
        for entry in table.table_data:
            entry[last_column] = '\n'.join(wrap(entry[last_column], max_width))
        self.file.write(table.table)
        self.file.write('\n')
