import numpy as np
import requests
import mysql.connector

import const

class mockSQLenv(object):
    """
    """
    def __init__(self, verbose=True, flag_reward = 10, query_reward = -1):
        # Get the action space
        self.A = np.array(const.actions)
        self.query_reward = query_reward
        self.flag_reward = flag_reward

        # init ctf database by escape type
        self.verbose = verbose
        self.escape_type = np.random.randint(0, const.MAX_ESC_TYPE)
        self.column_type = np.random.randint(const.MIN_COLUMN_TYPE, const.MAX_COLUMN_TYPE)
        self.db_config = const.db_config
        self.init_database()

        # Get the ip address of ctf envirnoment
        self.url = const.URL + 'ctf_{0}/ctf_{0}_{1}.php'.format(self.escape_type + 1, self.column_type)
        self.responce_success = const.RESONCE_SUCCESS

        # Get the set of actions that are syntactically correct
        self.syntaxmin = 0 + self.escape_type * 6
        self.syntaxmax = 6 + self.escape_type * 6

        self.termination = False
        if (self.verbose): print('Game setup with a random query')

    def step(self, action_number = None, action_string = None):
        # step() expects a correct action number or a correct action string. No checks in place

        # If given a string find out the action number
        if (action_number == None):
            print("action_number)", action_number)
            action_number = np.where(self.A == action_string)[0][0]
        if(self.verbose): print('I received action {0}: {1}'.format(action_number, self.A[action_number]))

        # Process action
        x = requests.post(self.url, data = {'id': action_string, 'pw': ''})
        if x.status_code == self.responce_success:
            if action_string in x.text:
                if(self.verbose): print('Responce is good but Query is syntactically wrong. I return 1')
                return 1, self.query_reward,self.termination,'Server response is 1'
            elif (action_number >= self.syntaxmin and action_number < self.syntaxmax):
                if 'collect column' in x.text:
                    if(self.verbose): print('Flag captured. I return 4')
                    self.termination = True
                    return 4, self.flag_reward,self.termination,'Server response is 4'
                else:
                    if(self.verbose): print('Correct exploratory action for the escape. I return 2')
                    return 2, self.query_reward,self.termination,'Server response is 2'
        elif (action_number >= self.syntaxmin and action_number < self.syntaxmax):
            if(self.verbose): print('Correct exploratory action for the escape but the column is wrong. I return 3')
            return 3, self.query_reward,self.termination,'Server response is 3'
        else:
            # server responce error
            if(self.verbose): print('Server responce error. I return 0')
            return 0, self.query_reward,self.termination,'Server response is 0'

    def reset(self):
        self.termination = False
        if(self.verbose): print('Game reset (but not reinitialized with a new random query!)')
        return None,0,self.termination,'Game reset'

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
                exit;
        except:
            print('Failed to set database up')
            exit;

    # def reveal_solution(self):
    #     #For debugging only
    #     print('Correct escapes are: \n [{0}]: {1} \n [{2}]: {3}'.format(self.setup[0],self.A[self.setup[0]],self.setup[1],self.A[self.setup[1]]))
    #     print('Correct SQL injection is: \n [{0}]: {1}'.format(self.setup[2],self.A[self.setup[2]]))
