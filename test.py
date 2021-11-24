import mysql.connector
import requests

url = 'http://127.0.0.1/'

config = {
    'user': 'root',
    'password': 'tiger',
    'host': 'localhost',
    'database': 'ctf'
}

users_data_1 = {
    (1, 'adam', 'MROcsm3', 0, '2017-01-01 00:00:00', 'hello'),
    (2, 'eve', 'fewc3m4tC', 0, '2017-01-01 00:00:00', 'pen'),
    (3, 'seccon', 'SECCON_4b', 1023, '2017-01-01 00:00:00', 'piece'),
    (4, 'lee', 'sin', 0, '2017-01-01 00:00:00', 'world'),
    (5, 'pat', 'goMFE', 0, '2017-01-01 00:00:00', 'pat'),
    (6, 'bob', 'bobobobob',0, '2017-01-01 00:00:00', 'nice'),
    (7, 'key', 'wordisSQLi',0, '2017-01-01 00:00:00', 'good')
}
users_data_2 = {
    (1, 1, 'MROcsm3', 0, '2017-01-01 00:00:00', 'hello'),
    (2, 2, 'fewc3m4tC', 0, '2017-01-01 00:00:00', 'pen'),
    (3, 3, 'SECCON_4b', 1023, '2017-01-01 00:00:00', 'piece'),
    (4, 4, 'sin', 0, '2017-01-01 00:00:00', 'world'),
    (5, 5, 'goMFE', 0, '2017-01-01 00:00:00', 'pat'),
    (6, 6, 'bobobobob',0, '2017-01-01 00:00:00', 'nice'),
    (7, 7, 'wordisSQLi',0, '2017-01-01 00:00:00', 'good')
}

query = 'INSERT INTO `users` (`id`, `loginid`, `password` ,`auth_bit`, `lasttime`, `comment`) VALUES (%s, %s, %s, %s, %s, %s)'

db = mysql.connector.connect(**config)

if db.is_connected():
    cursor = db.cursor();
    cursor.execute('DROP TABLE IF EXISTS users')
    # db.commit()
    cursor.execute("CREATE table users (id INT,loginid INT, password TEXT, auth_bit int, lasttime TIMESTAMP, comment TEXT)")
    # cursor.execute("CREATE table users (id INT,loginid TEXT, password TEXT, auth_bit int, lasttime TIMESTAMP, comment TEXT)")
    # db.commit()
    db.commit()
    for user in users_data_2:
        cursor.execute(query, user)
        db.commit()
    # records = cursor.fetchall()
    # for r in records:
    #     print(r)
else:
    print('false')

import const
import numpy as np

# for action in const.actions:
#     print(action)
escape_type = 3
column_type = 2
# escape_type = np.random.randint(1, 6)
# column_type = np.random.randint(2, 6)
url = const.url + 'ctf_{0}/ctf_{0}_{1}.php'.format(escape_type + 1, column_type)
syntaxmin = 0+escape_type*6
syntaxmax = 6+escape_type*6
# print(len(const.actions))
for action_number, action in enumerate(const.actions):

    x = requests.post(url, data = {'id': action, 'pw': ''})
    print(action)
    if x.status_code == 200:
        if action in x.text:
            print('Responce is good but Query is syntactically wrong. I return 1')
        elif (action_number >= syntaxmin and action_number < syntaxmax):
            if 'collect column' in x.text:
                print('\n')
                print('Flag captured. I return 4')
                break
            else:
                print('Correct exploratory action for the escape. I return 2')
    elif (action_number >= syntaxmin and action_number < syntaxmax):
        print('Correct exploratory action for the escape but the column is wrong. I return 3')
    else:
        # server responce error
        print('Error responce. I return 0')

print(url)
