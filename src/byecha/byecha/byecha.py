# -*- coding:utf-8 -*-

from .room import Room, RoomType
from .account import Account

import os
import requests
import re
import json
import time
import random
import base64
import urllib.parse

BASE_URL = 'https://www.chatwork.com'
LOGIN_URL = BASE_URL + '/login.php'
GATEWAY_URL = BASE_URL + '/gateway.php'

MAX_RETRY_CNT = 5
CHAT_SIZE = 40
INTERVAL_ORDER = 1.0


class ByeCha(object):
    ''' Chatworks log dumper '''
    def __init__(self, user_id, password, out_dir='_out'):
        ''' initializer '''
        self.user_id = user_id
        self.password = password
        self.session = requests.session()
        self.out_dir = out_dir
        random.seed()

        self._rooms = None
        self._contacts = None

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
            raise LookupError('ACCESS_TOKEN')
        self.token = token_all[0]

        myid_all = re.findall(r"var MYID *= *'(.+)';", res.text)
        if not myid_all or len(myid_all) <= 0:
            raise LookupError('MYID')
        self.myid = myid_all[0]

        # initialize
        self._init_load()

    def get_all_chat(self, room_id):
        # TODO really need to return all chat's list?
        first_id = 0
        chat_list = []
        chat_out_dir = os.path.join(self.out_dir, str(room_id))
        if not os.path.exists(chat_out_dir):
            os.makedirs(chat_out_dir)

        while True:
            tmp_list = self._load_old_chat(room_id, first_id)
            self.fetch_files(tmp_list)

            if first_id == 0:
                fname = str(room_id) + '_last.json'
            else:
                fname = str(room_id) + '_' + str(first_id) + '.json'
            fpath = os.path.join(chat_out_dir, fname)
            with open(fpath, 'w') as f:
                json.dump(tmp_list, f, ensure_ascii=False, indent=4)

            chat_list.extend(tmp_list)
            first_id = int(tmp_list[-1]['id'])
            if len(tmp_list) < CHAT_SIZE:
                break
            else:
                self._wait_interval()
        return chat_list

    def fetch_files(self, chat_list):
        for chat in chat_list:
            file_id_all = re.findall(r"\[download\:([^\]]+)\]", chat['msg'])
            for file_id in file_id_all:
                self._download_file(file_id)

    def _init_load(self):
        '''
        request 'init_load' command to load Chatworks settings
        '''
        res = self.session.get(GATEWAY_URL +
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
        result = res.json()['result']
        self.contact_dat = result['contact_dat']
        self.room_dat = result['room_dat']

        with open(os.path.join(self.out_dir, 'contact_dat.json'), 'w') as cf:
            json.dump(self.contact_dat, cf, ensure_ascii=False, indent=4)
        with open(os.path.join(self.out_dir, 'room_dat.json'), 'w') as rf:
            json.dump(self.room_dat, rf, ensure_ascii=False, indent=4)

        with open(os.path.join(self.out_dir, 'load_all.json'), 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def _load_old_chat(self, room_id, first_chat_id=0):
        '''
        request 'load_old_chat' command to get old chats on room
        '''
        cnt = 0
        while cnt < MAX_RETRY_CNT:
            try:
                res = self.session.get(GATEWAY_URL +
                                       '?cmd=load_old_chat' +
                                       '&myid=' + self.myid +
                                       '&_v=1.80a' +
                                       '&_av=5' +
                                       '&_t=' + self.token +
                                       '&ln=ja' +
                                       '&room_id=' + str(room_id) +
                                       '&last_chat_id=0' +
                                       '&first_chat_id=' + str(first_chat_id) +
                                       '&jump_to_chat_id=0' +
                                       '&unread_num=0' +
                                       '&file=1' +
                                       '&desc=1',
                                       timeout=(5, 1000))
                break
            except ConnectionError as ce:
                # count up
                cnt += 1
                if cnt >= MAX_RETRY_CNT:
                    # TODO logging retry over
                    raise ce
                else:
                    self._wait_interval()
            except TimeoutError as te:
                # TODO logging timeouts
                raise te

        status = res.json()['status']['success']
        if not status:
            raise ValueError('status')

        result = res.json()['result']
        return sorted(result['chat_list'],
                      key=lambda x: int(x['id']),
                      reverse=True)

    def _download_file(self, file_id):
        '''
        request 'download_file' command to get file info
        '''
        cnt = 0
        while cnt < MAX_RETRY_CNT:
            try:
                res = self.session.get(GATEWAY_URL +
                                       '?cmd=download_file' +
                                       '&bin=1' +
                                       '&file_id=' + str(file_id),
                                       timeout=(5, 10))
                break
            except ConnectionError as ce:
                # count up
                cnt += 1
                if cnt >= MAX_RETRY_CNT:
                    # TODO logging retry over
                    raise ce
                else:
                    self._wait_interval()
            except TimeoutError as te:
                # TODO logging timeouts
                raise te
        condis = res.headers['Content-disposition']
        filename_all = re.findall(r"attachment;filename\*=UTF-8''(.+)",
                                  condis)
        filename_old_all = re.findall(r"filename=\"=\?UTF-8\?B\?(.+)\?=\"",
                                      condis)
        if len(filename_all) > 0:
            filename = urllib.parse.unquote(filename_all[0])
        elif len(filename_old_all) > 0:
            filename = base64.b64decode(filename_old_all[0])
        else:
            raise Exception(condis)
        # if filename is instance of bytes
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        elif not isinstance(filename, str):
            raise Exception(filename)

        file_out_dir = os.path.join(self.out_dir, 'file_' + str(file_id))
        if not os.path.exists(file_out_dir):
            os.makedirs(file_out_dir)
        fpath = os.path.join(file_out_dir, filename)
        with open(fpath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=128):
                f.write(chunk)

    @property
    def rooms(self):
        ''' get all joined rooms '''
        if not self._rooms and self.room_dat:
            room_list = []
            for room_id in self.room_dat.keys():
                room_list.append(Room(self.myid,
                                      room_id,
                                      self.room_dat[room_id]))
            self._rooms = room_list
        return self._rooms

    @property
    def contacts(self):
        ''' get all accounts in contact '''
        if not self._contacts and self.contact_dat:
            contact_list = []
            for aid in self.contact_dat.keys():
                contact_list.append(Account(aid, self.contact_dat[aid]))
            self._contacts = contact_list
        return self._contacts

    def _wait_interval(self):
        time.sleep(INTERVAL_ORDER * random.uniform(1.0, 4.0))
