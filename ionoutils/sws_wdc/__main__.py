import argparse
from .archive import WDCArchive, WDC_ARCHIVE

parser = argparse.ArgumentParser()

parser.add_argument(
    '-d', '--dir',
    dest='archive_dir',
    type=str,
    default=WDC_ARCHIVE,
    help='The archive directory')
args = parser.parse_args()

wdca = WDCArchive(archive_dir=args.archive_dir)
wdca.read_archive()
# img = wdca.read_img('raw.png')
# print(img.shape)
# wdca.write_img('foo.png', img[:, :, 0])

# Test streak removal
# wdca.streak_threshold = 0.6
# img = wdca.read_img('raw4.png', remove_streaks=True)
# print(img.shape)
# wdca.write_img('raw4_no_streaks.png', img[:, :, 0])
