'''
Defines the base class for scaling parameter readers.
'''
from collections import OrderedDict
import os
import re

SCALING_VALUE_RE = re.compile('\d\d\d[A-Z/ ][A-Z/ ]')


class FiveDBase(object):

    PARAMETERS = {}

    def read_text(self, text: str) -> OrderedDict:
        '''Reads string and converts to dict of dicts.'''
        parameters = OrderedDict()
        for line in text.split('\n'):
            datestamp = line[:10]  # 1601010000 ie YYMMDDHHmm
            data = line[11:]
            values = re.findall(SCALING_VALUE_RE, data)
            if len(values) == len(self.PARAMETERS):
                d = OrderedDict()
                for index, value in enumerate(values):
                    number = int(value[:3])
                    qd = value[3:5]
                    d[self.PARAMETERS[index][0]] = (number * self.PARAMETERS[index][1], qd)
                parameters[datestamp] = d
            elif len(values) != 0:
                print('Invalid number of parameters', values)
        return parameters

    def read_file(self, dayfile, on_parameters_cb):
        # print(ID_TO_NAME[dayfile[-3:-1]], SONDTYPES[dayfile[-1:]])

        try:
            with open(dayfile, 'r') as f:
                for line in f:
                    datestamp = line[:10]
                    data = line[11:]
                    values = re.findall(SCALING_VALUE_RE, data)
                    d = OrderedDict()
                    for index, value in enumerate(values):
                        number = int(value[:3])
                        # qualifier = value[3]
                        # descriptor = value[4]
                        qd = value[3:5]
                        d[self.PARAMETERS[index][0]] = (number * self.PARAMETERS[index][1], qd)
                    on_parameters_cb(datestamp, d)

        except FileNotFoundError:
            # print('Missing', filename)
            pass

    def read_all(self, data_dir, on_parameters_cb):
        '''
        Reads all files in the given directory and calls the given callback.
        '''
        for dayfile in os.listdir(data_dir):
            self.read_file(dayfile, on_parameters_cb)
