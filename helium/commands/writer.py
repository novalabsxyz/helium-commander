import csv
import json
import abc
import terminaltables
import dpath.util as dpath
from textwrap import wrap


def for_format(format, file, **kwargs):
    json_opts = kwargs.pop('json', None)
    if format == 'json':
        json_opts = json_opts or {
            "indent": 4
        }
        return JSONWriter(file, json=json_opts, **kwargs)
    elif format == 'csv':
        json_opts = json_opts or {
            "indent": None
        }
        return CSVWriter(file, json=json_opts, **kwargs)
    elif format == 'tty':
        json_opts = json_opts or {
            "indent": 0
        }
        return TerminalWriter(file, json = json_opts, **kwargs)

class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file
        self.mapping = kwargs.pop('mapping', None)
        self.json_opts = kwargs.pop('json', None)

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
        if entries is None: return
        for entry in entries:
            row = { key: self.lookup(entry, path, json=self.json_opts)
                    for key, path in self.mapping.iteritems() }
            self.writer.writerow(row)


class JSONWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(JSONWriter, self).__init__(file, **kwargs)

    def start(self):
        self.file.write('[\n')
        self.is_first_entries = True

    def write_entries(self, entries):
        if entries is None: return
        for entry in entries:
            if self.is_first_entries:
                self.is_first_entries = False
            else:
                self.file.write(',')

            if self.mapping:
                entry = {key: self.lookup(entry, path) for key, path in self.mapping.iteritems() }

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

    def write_entries(self, entries):
        def map_entry(o):
            return [str(self.lookup(o, path, json=self.json_opts))
                    for _,path in self.mapping.items()]

        if entries is None: return
        if self.mapping:
            self.data.extend([map_entry(o) for o in entries])
        else:
            self.data.extend(entries)

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
