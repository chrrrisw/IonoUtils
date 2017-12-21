from ..vis.cleanreader import FiveDClean
from ..vis.rawreader import FiveDRaw, FiveDRawReadException
from ..vis.validreader import FiveDValid
from ..vis.sounders import SondLetters, ID_TO_PREFIX
from zipfile import ZipFile, BadZipFile
import os
from .validated import ValidScalingDB


WDC_ARCHIVE = '../ftp-out.ips.gov.au/wdc/wdc_ion_archive/'


class WDCArchive(object):
    """Finds and extracts matching raw and clean files."""

    def __init__(
            self,
            archive_dir=WDC_ARCHIVE,
            db_dir='.'):

        super(WDCArchive, self).__init__()

        self.archive_dir = archive_dir
        self.db_dir = db_dir
        self.rawreader = FiveDRaw()
        self.clnreader = FiveDClean()
        self.validreader = FiveDValid()

        self.sounders = set()

    def read_archive(self):
        for root, dirs, files in os.walk(self.archive_dir):
            *_, sounder, datatype, year = root.split(os.sep)
            self.sounders.add(sounder)
            if datatype in ['auto', 'cln', 'raw', 'valid']:
                print(f'Found {datatype} for {sounder} {year}')
                # if datatype == 'valid':
                #     self.process_valid(sounder, year, files)
                if datatype == 'auto':
                    self.process_auto(sounder, year, files)
                elif datatype == 'valid':
                    self.process_valid(sounder, year, files)
                elif datatype == 'cln':
                    self.process_clean(sounder, year, files)
                elif datatype == 'raw':
                    self.process_raw(sounder, year, files)

    # fields 1-2: station identification
    # field 3: sonde type
    # field 4: if the file is not a raw ionogram data file then this may be an
    #      'n', 'a', 'v'. An 'n' indicates these are cleaned ionograms so
    #      no processing need be done on these files except to expand them,
    #      an 'a' indicates the files are just autoscaled data files and a
    #      'v' indicates the files are autoscaled data files that have been
    #      validated to some extent.
    #      If the file is a raw ionogram data file then from this field will
    #      indicate the year, month, day and time fields.
    # fields 4-5(5-6): year for raw data (year for other archive file types)
    # fields 6-7(7-8): month for raw data (month for other archive file types)
    # fields 8-9(9-10): day for raw data (day for other archive file types)

    def _validate_filename(self, dir_sounder, dir_year, prefix, filename):
        valid = True
        station_id = None
        sonde_type = None
        month = None
        day = None
        if filename.endswith('.html'):
            valid = False
        elif filename == 'TRANS.TBL':
            valid = False
        elif prefix is not None:
            # Not raw file
            if filename[3] == prefix:
                station_id = filename[:2]
                sonde_type = filename[2]
                temp = ID_TO_PREFIX[station_id] + SondLetters[sonde_type].value
                if temp != dir_sounder:
                    print(f'\t### Station mismatch {temp} {dir_sounder}')
                    valid = False
                year = filename[4:8]
                if year != dir_year:
                    print(f'\t### Year mismatch {year} {dir_year}')
                    valid = False
                month = filename[8:10]
                if prefix == 'n':
                    # Clean data files only
                    day = filename[10:12]
            else:
                print(f'\t### File does not conform to naming standard {f}')
                valid = False
        else:
            # Raw file
            station_id = filename[:2]
            sonde_type = filename[2]
            try:
                temp = ID_TO_PREFIX[station_id] + SondLetters[sonde_type].value
            except KeyError as err:
                pass
            else:
                if temp != dir_sounder:
                    print(f'\t### Station mismatch {temp} {dir_sounder}')
                    valid = False
                year = filename[3:7]
                if year != dir_year:
                    print(f'\t### Year mismatch {year} {dir_year}')
                    valid = False
                month = filename[7:9]
                day = filename[9:11]

        return valid, station_id, sonde_type, month, day

    def process_auto(self, dir_sounder, dir_year, files):
        '''Process automatic scaling parameter files.

        For each file, validate the filename,
        '''
        for f in files:
            valid, station_id, sonde_type, month, day = self._validate_filename(
                dir_sounder, dir_year, 'a', f)
            if valid:
                print(f'\t{f} {station_id}, {sonde_type}, {dir_year}, {month}, {day}')

    def process_valid(self, dir_sounder, dir_year, files):
        '''Process validate scaling parameter files.

        For each file,
        '''
        for f in files:
            valid, station_id, sonde_type, month, day = self._validate_filename(
                dir_sounder, dir_year, 'v', f)
            if valid:
                print(f'\t{f} {station_id}, {sonde_type}, {dir_year}, {month}, {day}')

    def process_clean(self, dir_sounder, dir_year, files):
        '''Process cleaned ionograms.

        For each file,
        '''
        for f in files:
            valid, station_id, sonde_type, month, day = self._validate_filename(
                dir_sounder, dir_year, 'n', f)
            if valid:
                print(f'\t{f} {station_id}, {sonde_type}, {dir_year}, {month}, {day}')

    def process_raw(self, dir_sounder, dir_year, files):
        '''Process raw ionograms.

        For each file,
        '''
        for f in files:
            valid, station_id, sonde_type, month, day = self._validate_filename(
                dir_sounder, dir_year, None, f)
            if valid:
                print(f'\t{f} {station_id}, {sonde_type}, {dir_year}, {month}, {day}')

    def create_validated_db(self):
        validated_db = ValidScalingDB(os.path.join(self.db_dir, 'validated_scaling.db'))
        for root, dirs, files in os.walk(self.archive_dir):
            # _, _, _, _, sounder, datatype, year = root.split(os.sep)
            split_root = root.split(os.sep)
            if split_root[-2] == 'auto':
                pass
            elif split_root[-2] == 'cln':
                pass
            elif split_root[-2] == 'raw':
                pass
            elif split_root[-2] == 'valid':
                print(root)
                sounder = split_root[-3]
                year = split_root[-1]
                for f in files:
                    if f.endswith('zip'):
                        valid_zip_name = os.path.join(root, f)
                        print(f'Processing: {valid_zip_name}')

                        # valid_zip_name should be of form sstvyyyymm.zip
                        # ss = sounder
                        # t = sounder type
                        # v = valid
                        #
                        if f[3] == 'v':
                            y = f[4:8]
                            m = f[8:10]
                        else:
                            print(f'Unknown file: {f}')
                            continue

                        # if sounder not in self.validated:
                        #     self.validated[sounder] = {}
                        # if y not in self.validated[sounder]:
                        #     self.validated[sounder][y] = {}
                        # if m not in self.validated[sounder][y]:
                        #     self.validated[sounder][y][m] = []

                        try:
                            with ZipFile(valid_zip_name) as validated_zip:
                                # print(f, raw_zip.namelist())
                                for zipped_filename in validated_zip.namelist():
                                    if zipped_filename.startswith(y):
                                        yymmdd = datetime.datetime.strptime(zipped_filename[:7], '%Y%j')
                                        # print(f'{zipped_filename} {yymmdd.year} {yymmdd.month} {yymmdd.day}')

                                        # hh = zipped_filename[9:11]
                                        # mm = zipped_filename[12:14]

                                        with validated_zip.open(zipped_filename, 'r') as zipped_file:
                                            try:
                                                contents = zipped_file.read().decode()
                                                parms = self.validreader.read_text(contents)
                                                validated_db.add_scaling(sounder, parms)
                                            except FiveDRawReadException as exc:
                                                pass
                                            # else:
                                            #     self.raws[sounder][y][m][d].append(f'{hh}{mm}')
                                            #     self.rawreader.create_images(
                                            #         os.path.join(
                                            #             self.raw_output_dir,
                                            #             f'{sounder}_{y}_{m}_{d}_{hh}_{mm}'))
                                    else:
                                        print(f'Unknown file: {zipped_filename}')
                        except BadZipFile as exc:
                            print('NOT A VALID ZIP FILE', f)

        validated_db.close_connection()
