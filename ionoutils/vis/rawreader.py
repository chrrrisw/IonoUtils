import numpy as np
import os
from scipy.misc import imsave
import struct

'''
http://www.sws.bom.gov.au/World_Data_Centre/2/8/3
ftp://ftp-out.sws.bom.gov.au/wdc/wdc_ion_archive/
http://www.sws.bom.gov.au/World_Data_Centre/3/1/12

'''

CHANNEL_WIDTH = 20

class FiveDRawReadException(Exception):
    pass


class FiveDRaw(object):

    '''
    FiveDRaw reads raw data files generated from a 5D ionosonde.

    5D ionosonde raw data format

    An ionogram header of 32 bytes, followed by channel data.

    Each channel has:
      - a mini header of 8 bytes,
      - 512 bytes of O trace,
      - 4 bytes, and
      - 512 bytes of X trace.

    The total bytes of a 5D raw ionogram data file is:
    32 + 500(8 + 512 + 4 + 512) = 518032 bytes.
    '''

    FMT_HEADER = 'c3s8s6s4scc4s4s'
    FMT_CHANNEL_HEADER = '<hhBBh'
    FMT_TRACE = '512B'
    FMT_SPACE = 'BBh'  # media, max, ht_max??????????????????????????????????

    def __init__(self):
        super(FiveDRaw, self).__init__()
        self.offset = 0
        self.frequencies = []
        self.site = None
        self.date = None
        self.time = None
        self.num_channels = 0

    def _read_header(self, contents):
        '''
        Ionogram header in detail:

        Field     Size    Example/Format
        ID        1 byte
        SITE      3 bytes
        DATE      8 bytes YYYYMMDD
        TIME      6 bytes HHMMSS
        SONDE     4 bytes 5Df_
        MODE      1 byte  O, X, M, S
        PROCESS   1 bytes f, 8, 1
        NUM_CHANS 4 bytes
        SPARE     4 bytes
        '''
        header = struct.unpack_from(self.FMT_HEADER, contents, self.offset)
        self.offset += struct.calcsize(self.FMT_HEADER)

        self.site = header[1]
        self.date = header[2]
        self.time = header[3]
        if header[4] != b'  5D':
            raise FiveDRawReadException('Unexpected sonde in header', header[4])
        # print(header[0], header[5], header[6])
        self.num_channels = int(header[7])

    def _read_channel_header(self, contents):
        '''
        Read the channel header.

        Appends the frequency to the frequency list and return the height at
        which the maximum value occurs.

        The mini header which precedes each channel comprises 8 bytes, as follows.

        Field   Size
        FREQ    2b
        REG_NUM 2b
        MEDIAN  1b
        MAX     1b
        HT_MAX  2b
        '''
        freq, reg_num, median, mx, ht_max = struct.unpack_from(self.FMT_CHANNEL_HEADER, contents, self.offset)
        self.offset += struct.calcsize(self.FMT_CHANNEL_HEADER)
        self.frequencies.append(freq)
        # print('freq={}, reg_num={} median={} max={} ht_max={}'.format(freq, reg_num, median, mx, ht_max))
        if ht_max > 512:
            raise Exception('Unexpected ht_max')

        return ht_max

    def _read_space(self, contents):
        space = struct.unpack_from(self.FMT_SPACE, contents, self.offset)
        self.offset += struct.calcsize(self.FMT_SPACE)
        # print(np.median(space), np.max(space))
        # print(space)

        return space[2]

    def create_images(self, image_prefix, write_merged=False):
        '''Writes both O and X data to PNG files.'''

        temp = np.flipud(self.odata)
        imsave('{}_o.png'.format(image_prefix), temp)

        temp = np.flipud(self.xdata)
        imsave('{}_x.png'.format(image_prefix), temp)

        if write_merged:
            maxdata = np.maximum(self.odata, self.xdata)
            # argmaxdata = np.argmax(maxdata, axis=1)
            # print(maxdata.shape, argmaxdata.shape)
            # print(argmaxdata)
            # for i in range(500):
            #     maxdata[i, argmaxdata[i]] = 255
            temp = np.flipud(maxdata)
            imsave('{}_m.png'.format(image_prefix), temp)

    def read_bytearray(self, contents: bytearray):
        # Reset the frequency list, or it will continue to grow
        self.frequencies = []

        self.offset = 0
        self._read_header(contents)

        # num_channels frequency elements of 512 range depth
        # results in rotated ionogram
        self.odata = np.zeros([512, self.num_channels], np.uint8)
        self.xdata = np.zeros([512, self.num_channels], np.uint8)

        for channel_number in range(self.num_channels):
            ht_max = self._read_channel_header(contents)

            otrace = struct.unpack_from(self.FMT_TRACE, contents, self.offset)
            # print(np.median(otrace), np.max(otrace))
            self.odata[:, channel_number] = otrace
            # if highlight_max:
            #     self.odata[channel_number, ht_max] = 255
            self.offset += struct.calcsize(self.FMT_TRACE)

            ht_max = self._read_space(contents)

            xtrace = struct.unpack_from(self.FMT_TRACE, contents, self.offset)
            # print(np.median(xtrace), np.max(xtrace))
            self.xdata[:, channel_number] = xtrace
            # if highlight_max:
            #     self.xdata[channel_number, ht_max] = 255
            self.offset += struct.calcsize(self.FMT_TRACE)

        # print('RAW read finished at {}.'.format(self.offset))

    def read_file(self, filename: str, highlight_max: bool=False):
        with open(filename, 'rb') as f:
            contents = f.read()

        self.read_bytearray(contents)
