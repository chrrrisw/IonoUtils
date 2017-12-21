import os
import re
import argparse

FTPDIR = 'data/ftp-out.ips.gov.au/wdc/wdc_ion_archive'
INPUTDIR = 'data/input'


DATATYPES = ['auto', 'cln', 'raw', 'valid']

def main():
    parser = argparse.ArgumentParser(description="Read ionosonde files")

    parser.add_argument(
        dest='location')

    parser.add_argument(
        dest='sondtype')

    args = parser.parse_args()

    sondname = PREFIX[args.location] + args.sondtype

    sonddir = os.path.join(FTPDIR, sondname)

    # Get the first list of years
    years = [s for s in os.listdir(os.path.join(sonddir, DATATYPES[0])) if os.path.isdir(os.path.join(sonddir, DATATYPES[0], s))]
    # Create a set from it
    common_years = set(years)
    print(common_years)

    for dt in DATATYPES[1:]:

        years = [s for s in os.listdir(os.path.join(sonddir, dt)) if os.path.isdir(os.path.join(sonddir, dt, s))]
        common_years.intersection_update(years)
        print(sorted(years))

    print(common_years)
    for year in common_years:
        for dt in DATATYPES:
            datadir = os.path.join(sonddir, dt, year)
            print([s for s in os.listdir(datadir) if s.startswith(ID[args.location])])

    # print(DIRS)
    # for dirname in os.listdir(FTPDIR):
    #     found = False
    #     for prefix in DIRS.keys():
    #         if dirname.startswith(prefix):
    #             print('Found', prefix)
    #             found = True
    #     if not found:
    #         print('NOT Found', dirname)

if __name__ == '__main__':
    main()
