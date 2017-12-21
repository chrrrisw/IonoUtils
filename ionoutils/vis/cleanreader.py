import numpy as np
from scipy.misc import imsave
import struct

CHANNEL_WIDTH = 20


class FiveDClean(object):

    """docstring for FiveDClean"""

    # FMT_HEADER = '2s4s16s22s16s6s'
    FMT_HEADER = '66s'

    def __init__(self):
        super(FiveDClean, self).__init__()
        self.offset = 0

        self.frequencies = None
        self.num_channels = 0
        self.num_ranges = 0
        self.min_range = 0
        self.range_step = 0

        self.location = None
        self.datestamp = None
        self.year = None

        # The clean data array
        self.cdata = None
        # The image data array
        self.idata = None

    # def _create_images(self, f0F2):
    #     if f0F2 != 0:
    #         line = ((f0F2 // 1000) - self.frequencies[0]) // CHANNEL_WIDTH
    #         print(line)
    #         self.idata[line] = 255

    #         image_name = 'data/images/{}/{}-{}-cln-{}.png'.format(
    #             self.year, self.location, self.datestamp, self.polarisation)
    #         imsave(image_name, self.idata)

    def create_image(self, image_prefix: str):
        '''Writes the data to a PNG file.'''

        temp = np.flipud(self.cdata)
        imsave('{}.png'.format(image_prefix), temp)

    def _read_byte(self, contents: bytearray):
        b = struct.unpack_from('B', contents, self.offset)[0]
        self.offset += 1
        return b

    def _read_big_ushort(self, contents: bytearray):
        bus = struct.unpack_from('>H', contents, self.offset)[0]
        self.offset += 2
        return bus

    def _read_header(self, contents):
        '''Is this robust??? Should I look for 0x0a characters???'''

        header = struct.unpack_from(self.FMT_HEADER, contents, self.offset)
        self.offset += struct.calcsize(self.FMT_HEADER)

        # print(header)

        decoded_header = header[0].decode().split()
        fmt = decoded_header[0]
        # print('\tFormat:', fmt)
        self.num_channels = int(decoded_header[1])
        # print('\tNum frequencies (channels):', self.num_channels)
        self.min_range = float(decoded_header[2])  # km
        print('\tMin range:', self.min_range)
        self.range_step = float(decoded_header[3])
        print('\tRange step:', self.range_step)
        self.num_ranges = int(decoded_header[4])
        # print('\tNum ranges:', self.num_ranges)
        lat = decoded_header[5]
        lon = decoded_header[6]
        diplat = decoded_header[7]
        # print('\tLat/Lon/DipLat:', lat, lon, diplat)
        self.year = decoded_header[8]
        month = decoded_header[9]
        day = decoded_header[10]
        hrmin = decoded_header[11]
        self.datestamp = '{}-{}-{}-{}'.format(self.year, month, day, hrmin)
        self.location = decoded_header[12]

        # print('{} ({}, {}) {}-{}-{}:{}'.format(
        #     self.location, lat, lon, self.year, month, day, hrmin))
        # print('Frequencies: {}, Ranges: {}'.format(self.num_channels, self.num_ranges))

        self.cdata = np.zeros([self.num_ranges, self.num_channels], np.uint8)

    def _read_frequency_table(self, contents):

        # Pseudo-code for decoding frequencies:
        # 2 bytes for the start frequency
        # left shift 8 bits of the first byte and do bitwise OR with the second byte,
        # this will put their bytes one after the other to find the start frequency, as below
        # start_freq (kHz) = first byte << 8 | second byte
        # while(loop counter < number of frequencies i.e. N_FREQS)
        # {
        #   read the frequency step: 1 byte if < 255, else 3 bytes
        #   i.e. read a byte
        #   if byte < 255 then
        #       it is the frequency step
        #   else
        #       the next 2 bytes are the frequency step
        #   read the runlength: 1 byte if < 255, else 3 bytes
        #   i.e. read a byte
        #   if byte < 255 then
        #       it is runlength
        #   else
        #       the next 2 bytes are runlength
        #   loop counter = loop counter + runlength
        # }

        start_freq = self._read_big_ushort(contents)

        self.frequencies = [start_freq]
        loop_counter = 1
        while loop_counter < self.num_channels:
            next_byte = self._read_byte(contents)

            if next_byte < 255:
                freq_step = next_byte
            else:
                print('Frequency step is two bytes')
                freq_step = self._read_big_ushort(contents)

            next_byte = self._read_byte(contents)

            if next_byte < 255:
                run_length = next_byte
            else:
                print('Run length is two bytes')
                run_length = self._read_big_ushort(contents)
            # print(freq_step, run_length)

            for f in range(run_length + 1):
                self.frequencies.append(self.frequencies[-1] + freq_step)

            loop_counter += run_length + 1

        if len(self.frequencies) != self.num_channels:
            print('Number of frequencies', len(self.frequencies))
            print(self.frequencies)
            raise Exception('Unexpected number of frequencies.')

        # TODO: Uncomment when we want images written
        # self.width = (self.frequencies[-1] - self.frequencies[0]) // CHANNEL_WIDTH
        # self.idata = np.zeros([self.num_ranges, self.width + 1], np.uint8)

    def _read_channels(self, contents):

        for channel_number in range(self.num_channels):
            # TODO: This works for linearised data (e.g. idata)
            # x = (self.frequencies[channel_number] - self.frequencies[0]) // CHANNEL_WIDTH
            # average_amp, echo = self._read_channel(contents, x)
            average_amp, echo = self._read_channel(contents, channel_number)

        if self.offset != len(contents):
            raise Exception('Incorrect length')

    def _read_channel(self, contents, channel_number):
        echo = []

        data = self._read_byte(contents)

        average_amplitude = (data & 127) << 1

        echoCount = 0

        if (data & 128):
            # there are echoes
            lastrow = 0
            while True:
                echo.append({})
                # Read start =row
                row_offset = self._read_byte(contents)
                data = self._read_byte(contents)

                if (data & 128):
                    # ninth bit
                    row_offset += 256

                row = lastrow + row_offset

                echo[echoCount]['amp'] = (data & 127) << 1
                echo[echoCount]['row'] = row
                self.cdata[row, channel_number] = (data & 127) << 1
                # necho += 1

                # Get all the amplitudes
                while True:
                    row += 1
                    echoCount += 1
                    # necho += 1
                    echo.append({})

                    data = self._read_byte(contents)
                    echo[echoCount]['amp'] = (data & 127) << 1
                    echo[echoCount]['row'] = row
                    self.cdata[row, channel_number] = (data & 127) << 1

                    if (data & 128) != 0:
                        break

                echo[echoCount]['amp'] = echo[echoCount]['amp'] & 127
                self.cdata[row, channel_number] = self.cdata[row, channel_number] & 127
                if (echo[echoCount]['amp'] == 0):
                    # special case: runlength of 1
                    # necho += -1
                    row += -1
                else:
                    echoCount += 1

                lastrow = row

                if ((data & 64) != 0):
                    break

        return average_amplitude, echo

    def read_bytearray(self, contents: bytearray):
        self.offset = 0
        self._read_header(contents)

        self._read_frequency_table(contents)
        # print(self.frequencies)

        self._read_channels(contents)

        # self._create_images(f0F2)

    def read_file(self, filename, polarisation):
        with open(filename, 'rb') as f:
            contents = f.read()

        self.polarisation = polarisation

        self.read_bytearray(contents)
