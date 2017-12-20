'''
The classes in this module read validated scaling parameter files.

Currently only supports 5D ionosonde data.
'''

from .basescaling import FiveDBase


class FiveDValid(FiveDBase):

    '''Reads validated scaling parameters from a 5D ionosonde data files.'''

    PARAMETERS = {
        0: ('fmin', 10000),
        1: ('foE', 10000),
        2: ('hE', 1.00),
        3: ('foEs', 100000),
        4: ('fbEs', 100000),
        5: ('hEs', 1.00),
        6: ('foF1', 100000),
        7: ('hF', 1.00),
        8: ('foF2', 100000),
        9: ('fxI', 100000),
        10: ('hF2', 1.00),
        11: ('M3000F2', 0.01),
        12: ('huh1', 1),
        13: ('huh2', 1),
        14: ('MUF', 100000)
    }

    def __init__(self):
        super(FiveDValid, self).__init__()
