import torch

# Server
URL = 'http://127.0.0.1/'
RESONCE_SUCCESS = 200

# Reward
QUERY_REWARD = -1
FLAG_REWARD = 10

# Database
MAX_ESC_TYPE = 4
MIN_COLUMN_TYPE = 2
MAX_COLUMN_TYPE = 6

# Neural Agent
MAX_VOCAB_SIZE = 10000
UPDATE_FREQUENCY = 20
LOG_FREQUENCY = 100
GAMMA = 0.8

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

db_config = {
    'user': 'root',
    'password': 'tiger',
    'host': 'localhost',
    'database': 'ctf'
}
users_dataset_text = {
    (1, 'adam', 'MROcsm3', 0, '2017-01-01 00:00:00', 'hello'),
    (2, 'eve', 'fewc3m4tC', 0, '2017-01-01 00:00:00', 'pen'),
    (3, 'seccon', 'SECCON_4b', 1023, '2017-01-01 00:00:00', 'piece'),
    (4, 'lee', 'sin', 0, '2017-01-01 00:00:00', 'world'),
    (5, 'pat', 'goMFE', 0, '2017-01-01 00:00:00', 'pat'),
    (6, 'bob', 'bobobobob',0, '2017-01-01 00:00:00', 'nice'),
    (7, 'key', 'wordisSQLi',0, '2017-01-01 00:00:00', 'good')
}
users_dataset_int = {
    (1, 1, 'MROcsm3', 0, '2017-01-01 00:00:00', 'hello'),
    (2, 2, 'fewc3m4tC', 0, '2017-01-01 00:00:00', 'pen'),
    (3, 3, 'SECCON_4b', 1023, '2017-01-01 00:00:00', 'piece'),
    (4, 4, 'sin', 0, '2017-01-01 00:00:00', 'world'),
    (5, 5, 'goMFE', 0, '2017-01-01 00:00:00', 'pat'),
    (6, 6, 'bobobobob',0, '2017-01-01 00:00:00', 'nice'),
    (7, 7, 'wordisSQLi',0, '2017-01-01 00:00:00', 'good')
}
