from enum import Enum

# Station                    Directory/Prefix      Station ID
STATIONS = [
    ('Auckland',             'auk',                'au'),
    ('Biak',                 'bik',                'bk'),
    ('Brisbane',             'bri',                'br'),
    ('Bundoora',             'bundoora',           'bu'),
    ('Camden',               'cdn',                'cn'),
    ('Canberra',             'cbr',                'cb'),
    ('Casey',                'cas',                'cy'),
    ('Christchurch',         'cch',                'cc'),
    ('Cocos Islands',        'cck',                'co'),
    ('Concepcion',           'concepcion',         'cp'),
    ('Darwin',               'dwn',                'dw'),
    ('Davis',                'dav',                'dv'),
    ('Hobart',               'hbt',                'hb'),
    ('Islamabad',            'islamabad',          'is'),
    ('Karachi',              'karachi',            'ka'),
    ('Kiruna',               'kir',                'ki'),
    ('Kokubunji',            'kok',                'ko'),
    # ('Learmonth 5D',         'lea5d',              'lm'),
    # ('Learmonth',            'lth',                'lm'),
    ('Learmonth 5D',         'lea',                'lm'),
    ('Lycksele',             'lycks',              'ly'),
    ('Macquarie Island',     'mac',                'mq'),
    ('Manila',               'man',                'mn'),
    ('Mawson',               'maw',                'mw'),
    ('Multan',               'multan',             'mu'),
    ('Mundaring',            'mun',                'md'),
    ('Niue',                 'nue',                'nu'),
    ('Norfolk Island',       'nlk',                'nf'),
    ('Okinawa',              'oki',                'ok'),
    ('Perth 5D',             'per5d',              'pe'),
    ('Port Moresby',         'pom',                'pm'),
    ('Salisbury',            'sal',                'sl'),
    ('Scott Base',           'sct',                'sc'),
    ('Townsville',           'tvl',                'tv'),
    ('Uppsala',              'upp',                'up'),
    ('Vanimo',               'vno',                'vn'),
    ('Wakkanai',             'wak',                'wa'),
    ('Yamagawa',             'yam',                'ya'),
]

NAME_TO_PREFIX = {s[0]: s[1] for s in STATIONS}
NAME_TO_ID = {s[0]: s[2] for s in STATIONS}
PREFIX_TO_NAME = {s[1]: s[0] for s in STATIONS}
PREFIX_TO_ID = {s[1]: s[2] for s in STATIONS}
ID_TO_NAME = {s[2]: s[0] for s in STATIONS}
ID_TO_PREFIX = {s[2]: s[1] for s in STATIONS}


class SondLetters(Enum):
    a = '4a'
    b = '4b'
    c = '4c'
    d = '4d'
    e = '5a'
    f = '5b'
    g = '5c'
    h = '5d'
    i = 'cadi'
    j = 'lowell'
    k = 'swedish'
    l = 'kel51'
    m = 'japanese'
