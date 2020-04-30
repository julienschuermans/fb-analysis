import os

DATA_DIR = 'data'
MSG_DIR = os.path.join(DATA_DIR, 'messages/inbox')
MY_NAME = 'Mark Zuckerberg'

BORING_WORDS = {
    'jij', 'wel', 'nee', 'ok', 'heel', 'ga', 'oke', 'gaat', 'gaan',
    'doe', 'laat', 'weer', 'beetje', 'net', 'ofzo', 'ah', 'gij', 'ha',
    'gewoon', 'denk', 'evt',
    '..', '‘', '’', '...', '....', "n't", "'s", "'m", "'ll", 'http', 'https', "'re", "'ve", "''", "``"
}
