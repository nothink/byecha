# -*- coding:utf-8 -*-

import requests
import re
import json

BASE_URL = 'https://www.chatwork.com'


class ByeCha(object):
    ''' Chatworks log dumper '''
    def __init__(self, user_id, password):
        ''' initializer '''
        self.user_id = user_id
        self.password = password
        self.session = requests.session()

    def login(self):
        '''
        login Chatworks, and get token and myid
        '''
        login_url = BASE_URL + '/login.php'
        res = self.session.post(login_url,
                                {'email': self.user_id,
                                 'password': self.password,
                                 'autologin': 'on'})
        # TODO when status code is 302
        token_all = re.findall(r"var ACCESS_TOKEN *= *'(.+)';", res.text)
        if not token_all or len(token_all) <= 0:
            raise LookupError('ACCESS_TOKEN')
        self.token = token_all[0]

        myid_all = re.findall(r"var MYID *= *'(.+)';", res.text)
        if not myid_all or len(myid_all) <= 0:
            raise LookupError('MYID')
        self.myid = myid_all[0]

        # initialize
        self._init_load()

    def _init_load(self):
        '''
        initialize Chatworks settings
        '''
        init_url = BASE_URL + '/gateway.php'
        res = self.session.get(init_url +
                               '?cmd=init_load' +
                               '&myid=' + self.myid +
                               '&_v=1.80a' +
                               '&_av=5' +
                               '&_t=' + self.token +
                               '&ln=ja' +
                               '&rid=0' +
                               '&type=' +
                               '&new=1')
        status = res.json()['status']['success']
        if not status:
            raise ValueError('status')
        self.contacts = res.json()['result']['contact_dat']
        self.rooms = res.json()['result']['room_dat']
        print(self.contacts)
        print(self.rooms)
