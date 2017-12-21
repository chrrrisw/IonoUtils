from .archive import WDCArchive

wdca = WDCArchive()
wdca.read_archive()
# img = wdca.read_img('raw.png')
# print(img.shape)
# wdca.write_img('foo.png', img[:, :, 0])

# Test streak removal
# wdca.streak_threshold = 0.6
# img = wdca.read_img('raw4.png', remove_streaks=True)
# print(img.shape)
# wdca.write_img('raw4_no_streaks.png', img[:, :, 0])
