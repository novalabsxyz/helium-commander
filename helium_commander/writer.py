import abc

import dpath.util as dpath
import csv
import json

def add_writer_arguments(parser):
    parser.add_argument('--format', default='csv', choices=['csv', 'json'],
                        help='The output format for the results (default \'csv\')')

def writer_for_opts(opts, file, **kwargs):
    if opts.format == 'json':
        return JSONWriter(file, **kwargs)
    elif opts.format == 'csv':
        return CSVWriter(file, **kwargs)


class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file

    def start(self):
        return

    @abc.abstractmethod
    def write_readings(self, readings):
        return

    def finish(self):
        return

class CSVWriter(BaseWriter):
    def __init__(self, file, **kwargs):
        super(CSVWriter, self).__init__(file, **kwargs)
        self.mapping = kwargs['mapping']
        self.writer = csv.DictWriter(file, self.mapping.keys())

    def start(self):
        self.writer.writeheader()

    def write_readings(self, readings):
        if readings is None: return
        for reading in readings:
            row = { key: dpath.get(reading, path) for key, path in self.mapping.iteritems() }
            self.writer.writerow(row)


class JSONWriter(BaseWriter):
    def start(self):
        self.file.write('[')
        self.is_first_readings = True

    def write_readings(self, readings):
        for reading in readings:
            if self.is_first_readings:
                self.is_first_readings = False
            else:
                self.file.write(',')
            self.file.write(json.dumps(reading))

    def finish(self):
        self.file.write(']')
