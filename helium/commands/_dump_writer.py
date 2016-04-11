import abc

import dpath.util as dpath
import csv
import json

def writer_for_format(format, file, **kwargs):
    if format == 'json':
        return JSONWriter(file, **kwargs)
    elif format == 'csv':
        return CSVWriter(file, **kwargs)


class BaseWriter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, file, **kwargs):
        self.file = file

    def process_timeseries(self, service, sensor_id, **kwargs):
        def json_data(json):
            return json['data'] if json else None
        # Get the first page
        res = service.get_sensor_timeseries(sensor_id, **kwargs)
        self.start()
        self.write_readings(json_data(res))
        while res != None:
            res = service.get_prev_page(res)
            self.write_readings(json_data(res))
        self.finish()

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
        if readings is None: return
        for reading in readings:
            if self.is_first_readings:
                self.is_first_readings = False
            else:
                self.file.write(',')
            self.file.write(json.dumps(reading))

    def finish(self):
        self.file.write(']')
