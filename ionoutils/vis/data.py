from . import sounders
from .autoreader import FiveDAuto
from .cleanreader import FiveDClean
from .rawreader import FiveDRaw
from .validreader import FiveDValid
from bisect import bisect_left
from enum import Enum
import argparse
import os


class Polarisation(Enum):
    O = 0
    X = 1


class Data(Enum):
    Clean = 0
    Raw = 1


INPUT_DIR = 'data/input'


class IonReader(object):

    """Co-ordinates reading of various ionosonde data files."""

    def __init__(self, siteprefix, sondtype, year, sonddir):
        super(IonReader, self).__init__()
        self.site = siteprefix
        self.sondtype = sondtype
        self.year = year

        self.sonddir = sonddir
        self.sondid = sounders.PREFIX_TO_ID[self.site]
        self.sondletter = sounders.SondLetters(sondtype)

        self.data = {}

        self.rawreader = FiveDRaw()
        self.cleanreader = FiveDClean()

    def auto_name_of(self, datestamp):
        # 2016001a.cbh

        # convert datestamp to doy

        return f'{year}{doy:03d}a.{self.sondid}{self.sondletter.name}'

    def valid_name_of(self, datestamp):
        # 2016001v.cbh
        return f'{year}{doy:03d}v.{self.sondid}{self.sondletter.name}'

    def raw_name_of(self, datestamp):
        # cbh16010100.00
        return f'{self.sondid}{self.sondletter.name}{datestamp[:8]}.{datestamp[8:]}'

    def clean_name_of(self, datestamp, polarisation):
        # CO1603022255  CX1601022300
        return f'C{polarisation.name}{datestamp}'

    def on_auto_read(self, datestamp, scaling_parameters):
        '''
        The callback for the automatic scaling data.
        '''

        # print('a1 {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
        #     datestamp,
        #     scaling_parameters['foE'][0],
        #     scaling_parameters['foF1'][0],
        #     scaling_parameters['foF2'][0]))
        if datestamp not in self.data:
            self.data[datestamp] = {}
        self.data[datestamp]['auto'] = scaling_parameters
        # print('a2 {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
        #     datestamp,
        #     self.data[datestamp]['auto']['foE'][0],
        #     self.data[datestamp]['auto']['foF1'][0],
        #     self.data[datestamp]['auto']['foF2'][0]))

    def on_valid_read(self, datestamp, scaling_parameters):
        '''
        The callback for the validated scaling data.
        '''

        # print('v1 {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
        #     datestamp,
        #     scaling_parameters['foE'][0],
        #     scaling_parameters['foF1'][0],
        #     scaling_parameters['foF2'][0]))
        if datestamp not in self.data:
            self.data[datestamp] = {}
        self.data[datestamp]['valid'] = scaling_parameters
        # if 'auto' in self.data[datestamp]:
        #     print('va {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
        #         datestamp,
        #         self.data[datestamp]['auto']['foE'][0],
        #         self.data[datestamp]['auto']['foF1'][0],
        #         self.data[datestamp]['auto']['foF2'][0]))
        # print('v2 {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
        #     datestamp,
        #     self.data[datestamp]['valid']['foE'][0],
        #     self.data[datestamp]['valid']['foF1'][0],
        #     self.data[datestamp]['valid']['foF2'][0]))

    def read_scaling_parameters(self):
        '''
        Reads both the auto and validated scaling data files.
        '''

        valid_dir = os.path.join(INPUT_DIR, self.sonddir, 'valid', self.year)
        validreader = FiveDValid()

        auto_dir = os.path.join(INPUT_DIR, self.sonddir, 'auto', self.year)
        autoreader = FiveDAuto(auto_dir)

        for doy in range(1, 367):
            # TODO: Only copes with 5d sounders 'h'
            if autoreader:
                afn = '{}{:03d}a.{}{}'.format(self.year, doy, self.sondid, 'h')
                autoreader.read(afn, self.on_auto_read)
            if validreader:
                vfn = os.path.join(
                    valid_dir,
                    '{}{:03d}v.{}{}'.format(self.year, doy, self.sondid, 'h'))
                validreader.read_file(vfn, self.on_valid_read)

        self.datestamps = sorted(self.data.keys())

    def read_clean(self, datestamp, polarisation):
        '''
        Return the clean data for the given date and polarisation.
        '''

        clean_file = os.path.join(
            INPUT_DIR,
            self.sonddir,
            'cln',
            self.year,
            self.clean_name_of(datestamp, polarisation))

        if os.path.exists(clean_file):
            self.cleanreader.read_file(clean_file, polarisation)
            return self.cleanreader.cdata
        else:
            return None

        # for datestamp in self.data:
        #     if 'valid' in self.data[datestamp]:
        #         co = os.path.join(cln_dir, 'CO'+datestamp)
        #         cx = os.path.join(cln_dir, 'CX'+datestamp)
        #         if os.path.exists(co):
        #             print('found', co, self.data[datestamp]['valid']['foF2'][0])
        #             self.cleanreader.convert_to_images('CO'+datestamp, self.data[datestamp]['valid']['foF2'][0])
        #         # else:
        #         #     print('absent', co, self.data[datestamp]['valid']['foF2'][0])
        #         if os.path.exists(cx):
        #             print('found', cx, self.data[datestamp]['valid']['foF2'][0])
        #         # for fn in sorted(os.listdir(cln_dir)):
        #         #     # Filenames of form xxYYMMDDHHmm where xx is CO or CX
        #         #     # print(fn)
        #         #     if fn[2:] in clean_dates:
        #         #         print('CLEAN', fn)
        #         #         self.cleanreader.convert_to_images(fn, f0F2s[clean_dates.index(fn[2:])])

    def read_raw(self, datestamp, polarisation):
        '''
        Return the raw data for the given date and polarisation.
        '''

        raw_file = os.path.join(
            INPUT_DIR,
            self.sonddir,
            'raw',
            self.year,
            self.raw_name_of(datestamp))

        if os.path.exists(raw_file):
            self.rawreader.read_file(raw_file)
            if polarisation == Polarisation.O:
                return self.rawreader.odata
            else:
                return self.rawreader.xdata
        else:
            return None

    def height_to_index(self, height):
        # min range = 80km
        # range step = 1.2km
        return (height - 80) / 1.2

    def freq_to_index(self, freq_hz, data=Data.Clean):
        """
        Assumes frequencies is sorted. Returns closest value to freq_hz.

        If two numbers are equally close, return the smallest number.
        """
        if data == Data.Clean:
            frequencies = self.cleanreader.frequencies
        else:
            frequencies = self.rawreader.frequencies

        pos = bisect_left(frequencies, freq_hz // 1000)
        # if pos == 0:
        #     return frequencies[0]
        # if pos == len(frequencies):
        #     return frequencies[-1]
        # before = frequencies[pos - 1]
        # after = frequencies[pos]
        # if after - freq_hz < freq_hz - before:
        #     return after
        # else:
        #     return before
        # print(pos, frequencies[pos], freq_hz // 1000, frequencies[pos + 1])
        return pos

    # def freq_to_index(self, freq_hz, data=Data.Clean):
    #     if data == Data.Clean:
    #         frequencies = self.cleanreader.frequencies
    #     else:
    #         frequencies = self.rawreader.frequencies

    #     for index, value in enumerate(frequencies):
    #         if (value * 1000) > freq_hz:
    #             # print(index, freq_hz // 1000, value - 1)
    #             return index - 1
    #     return index

    def compare_auto_valid(self):
        for datestamp in self.data:
            if 'auto' in self.data[datestamp] and 'valid' in self.data[datestamp]:
                if self.data[datestamp]['valid']['MUF'][0] != 0:
                    print(self.data[datestamp]['valid'])
                # print('a {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
                #     datestamp,
                #     self.data[datestamp]['auto']['foE'][0],
                #     self.data[datestamp]['auto']['foF1'][0],
                #     self.data[datestamp]['auto']['foF2'][0]))
                # print('v {} foE {:9d} Hz, foF1 {:9d} Hz, foF2 {:9d} Hz'.format(
                #     datestamp,
                #     self.data[datestamp]['valid']['foE'][0],
                #     self.data[datestamp]['valid']['foF1'][0],
                #     self.data[datestamp]['valid']['foF2'][0]))


def main():
    parser = argparse.ArgumentParser(description="Read ionosonde files")

    parser.add_argument(
        '-c',
        action='store_true',
        dest='clean',
        default=False,
        help='Generate clean images')

    parser.add_argument(
        dest='siteprefix')

    parser.add_argument(
        dest='sondtype')

    parser.add_argument(
        dest='sonddir')

    parser.add_argument(
        dest='year')

    args = parser.parse_args()

    ir = IonReader(args.siteprefix, args.sondtype, args.year, args.sonddir)
    ir.read_scaling_parameters()
    ir.compare_auto_valid()
    if args.clean:
        data = ir.read_clean('0901010000', Polarisation.O)
        print(data.shape)
        from scipy.misc import imsave

        imsave('foo.png', data)


if __name__ == '__main__':
    main()
