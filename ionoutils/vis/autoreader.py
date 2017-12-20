'''
The classes in this module read auto-scaled parameter files.

Currently only supports 5D ionosonde data.
'''

import os
import re
from .basescaling import FiveDBase, SCALING_VALUE_RE


class FiveDAuto(FiveDBase):

    '''Reads automatic scaling parameters from a 5D ionosonde data files.'''

    PARAMETERS = {
        0: ('fmin', 10000),
        1: ('foE', 10000),
        2: ('hE', 1.00),
        3: ('foEs', 100000),
        4: ('fbEs', 100000),
        5: ('hEs', 1.00),
        6: ('foF1', 100000),
        7: ('hF1', 1.00),
        8: ('foF2', 100000),
        9: ('foI', 100000),
        10: ('hF2', 1.00),
        11: ('M3000', 0.01),
        12: ('MUF', 100000),
    }

    def __init__(self):
        super(FiveDAuto, self).__init__()

    def find_clean_data(self, data_dir):
        no_qualifiers = []
        foF2 = []

        for fn in os.listdir(data_dir):
            filename = os.path.join(data_dir, fn)
            # print(ID_TO_NAME[fn[-3:-1]], SONDTYPES[fn[-1:]])
            with open(filename, 'r') as f:
                for line in f:
                    # datestamp = '20{}-{}-{} {}:{}'.format(
                    #     line[0:2],
                    #     line[2:4],
                    #     line[4:6],
                    #     line[6:8],
                    #     line[8:10])  # YYMMDDHHmm
                    datestamp = line[:10]
                    data = line[11:]
                    values = re.findall(SCALING_VALUE_RE, data)
                    all_valid = True
                    for index, value in enumerate(values):
                        number = int(value[:3])
                        qualifier = value[3]
                        descriptor = value[4]
                        if qualifier != '/' and qualifier != ' ':
                            all_valid = False
                        if descriptor != '/' and descriptor != ' ':
                            all_valid = False

                    if all_valid:
                        d = dict(zip(self.PARAMETERS, values))
                        # print('{} {} {} {} {}'.format(fn, d['foE'], d['foEs'], d['foF1'], d['foF2']))
                        no_qualifiers.append(datestamp)
                        foF2.append(d['foF2'])

        return no_qualifiers, foF2
