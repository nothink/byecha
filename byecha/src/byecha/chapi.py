# -*- coding:utf-8 -*-

# from .room import Room, RoomType
from .const import *

import re
from datetime import datetime, timedelta
import time

import requests
from requests.exceptions import ConnectionError, ReadTimeout


class ChaPi(object):
    '''
    Chatworks API Accessor
    '''
    def __init__(self, user_id, password):
        '''
        initializer
        '''
        self.user_id = user_id
        self.password = password

        self.api_limit = 1
        self.api_current = 1
        self.api_reset_time = datetime.max

        self.session = requests.session()
        self.login()

    def login(self):
        '''
        login Chatworks, and get token and myid
        '''
        res = self.session.post(LOGIN_URL,
                                {'email': self.user_id,
                                 'password': self.password,
                                 'autologin': 'on'})
        # TODO when status code is 302
        token_all = re.findall(r"var ACCESS_TOKEN *= *'(.+)';", res.text)
        if not token_all or len(token_all) <= 0:
            raise LookupError('ACCESS_TOKEN (maybe, login error)')
        self.token = token_all[0]

        myid_all = re.findall(r"var MYID *= *'(.+)';", res.text)
        if not myid_all or len(myid_all) <= 0:
            raise LookupError('MYID')
        self.myid = myid_all[0]

    def get_token(self):
        '''
        Get API Token from api page
        '''
        ecf_sec_ptn = re.compile(r"<input type=\"hidden\" name=\"ecf_security_token_api_token\" value=\"([0-9abcdef]*)\">")

        res = self.session.get(TOKEN_PUBLUSHER_URL)
        m = ecf_sec_ptn.search(res.text)
        ecf_sec_token = m.group(1)

        api_tkn_ptn = re.compile(r"<input name=\"token\" type=\"text\" id=\"token\" readonly=\"readonly\" class=\"inputLong\" value=\"([0-9a-f]*)\" />")

        res = self.session.post(TOKEN_PUBLUSHER_URL,
                        {'password': self.password,
                         'display': '表示',
                         'ecf_security_token_api_token': ecf_sec_token})
        m = api_tkn_ptn.search(res.text)
        self.api_token = m.group(1)
        return self.api_token

    def get_me(self, api_token=None):
        if api_token:
            self.api_token = api_token
        res = self._get_from_rest('/me')
        return res.text

    def get_rooms(self):
        '''
        Get room list
        '''
        res = self._get_from_rest('/rooms')
        return res.json()

    def get_messages(self, room_id):
        '''
        Get message list (the latest 100 msgs only)
        '''
        res = self._get_from_rest('/rooms/' + str(room_id) + '/messages')
        if not res.text:
            return None
        return res.json()

    def delete_message(self, room_id, message_id):
        res = self._delete_to_rest('/rooms/' + str(room_id) + '/messages/' + str(message_id))
        if not res.text:
            return None
        return res.json()

    def _get_from_rest(self, endpoint='/', param=None):
        '''
        GET request using REST API
        '''
        if self.api_current == 0:
            self._sleep_to(self.api_reset_time)
        cnt = 0
        while cnt < MAX_RETRY_CNT:
            try:
                url =API_ENDPOINT_URL + endpoint
                if param:
                    param_list = []
                    for key in param:
                        param_list.append(key + '=' + str(param[key]))
                    query = '&'.join(param_list)
                    url = url  + '?' + query
                res = self.session.get(url,
                                       headers = {'X-ChatWorkToken': self.api_token},
                                       timeout=(5, 10 * 60))
                self.api_limit, self.api_current, self.api_reset_time = self._check_rate_limit(res)
                if self.api_current > 1:
                    break
                else:
                    self._sleep_to(self.api_reset_time)
                    break
            except (ConnectionError, ReadTimeout) as e:
                print('raised: ' + e.__class__.__name__ + ' , cnt:' + str(cnt))
        return res

    def _delete_to_rest(self, endpoint='/', param=None):
        '''
        DELETE request using REST API
        '''
        if self.api_current == 0:
            self._sleep_to(self.api_reset_time)
        cnt = 0
        while cnt < MAX_RETRY_CNT:
            try:
                url =API_ENDPOINT_URL + endpoint
                if param:
                    param_list = []
                    for key in param:
                        param_list.append(key + '=' + str(param[key]))
                    query = '&'.join(param_list)
                    url = url  + '?' + query
                res = self.session.delete(url,
                                          headers = {'X-ChatWorkToken': self.api_token},
                                          timeout=(5, 10 * 60))
                self.api_limit, self.api_current, self.api_reset_time = self._check_rate_limit(res)
                if self.api_current > 1:
                    break
                else:
                    self._sleep_to(self.api_reset_time)
                    break
            except (ConnectionError, ReadTimeout) as e:
                print('raised: ' + e.__class__.__name__ + ' , cnt:' + str(cnt))
        return res

    def _check_rate_limit(self, response):
        h = response.headers
        limit = 0
        current = 0
        reset_time = datetime.min
        if 'X-RateLimit-Limit' in h:
            limit = int(h['X-RateLimit-Limit'])
        if 'X-RateLimit-Remaining' in h:
            current = int(h['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in h:
            reset_time = datetime.fromtimestamp(int(h['X-RateLimit-Reset']))
        return (limit, current, reset_time)

    def _sleep_to(self, next_datetime):
        now_dt = datetime.now()
        if next_datetime > now_dt:
            print('next: ' + str(next_datetime))
            delta = next_datetime - now_dt
            time.sleep(delta.total_seconds() + 0.1)
