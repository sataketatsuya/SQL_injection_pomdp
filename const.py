import generate_actions

# Server
url = 'http://127.0.0.1/'
responce_success = 200

# Actions
actions = generate_actions.generate_actions()

# Database
max_esc_type = 6
min_column_type = 2
max_column_type = 6

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
