# -*- coding:utf-8 -*-

# from .room import Room, RoomType
from .const import *

import os
import re
import json
import time
import random
import base64
import urllib.parse
import shutil

import requests
from requests.exceptions import ConnectionError, ReadTimeout


class ByeCha(object):
    '''
    Chatworks log dumper
    '''
    def __init__(self, user_id, password, out_dir='_out'):
        '''
        initializer
        '''
        self.user_id = user_id
        self.password = password
        self.session = requests.session()
        self.root = out_dir
        random.seed()

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
        with open(os.path.join(self.root, MYID_FILE), 'w') as f:
            f.write(self.myid)

        # initialize
        self._init_load()

        # get avatar icons and room icons
        self.fetch_avatars()
        self.fetch_room_icons()

    def fetch_all_chat(self, room_id):
        '''
        get all chats, and dump in files, and download attached files in a room
        '''
        first_id = 0
        output_dir = os.path.join(self.root, str(room_id))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        while True:
            tmp_list = self._load_old_chat(room_id, first_id)
            self.fetch_files(tmp_list)
            self.fetch_previews(tmp_list)

            if first_id == 0:
                fname = str(room_id) + '_last.json'
            else:
                fname = str(room_id) + '_' + str(first_id) + '.json'
            fpath = os.path.join(output_dir, fname)
            with open(fpath, 'w') as f:
                json.dump(tmp_list, f, ensure_ascii=False, indent=4)

            # MAX_CHAT_SIZE is size that we can fetch max
            first_id = int(tmp_list[-1]['id'])
            if len(tmp_list) < MAX_CHAT_SIZE:
                break
            else:
                self._wait_interval()

    def fetch_files(self, chat_list):
        '''
        fetch files in list of chat
        '''
        for chat in chat_list:
            file_id_all = re.findall(r"\[download\:([^\]]+)\]", chat['msg'])
            for file_id in file_id_all:
                self._download_file(file_id)
                self._wait_interval()

    def fetch_previews(self, chat_list):
        for chat in chat_list:
            file_id_all = re.findall(r"\[preview id=(\d*) ht=(\d*)\]",
                                     chat['msg'])
            for file_id in file_id_all:
                self._download_preview(file_id)
                self._wait_interval()

    def fetch_avatars(self):
        for aid in self.contact_dat:
            if 'av' in self.contact_dat[aid]:
                av = self.contact_dat[aid]['av']
                url = AVATAR_BASE_URL + av
                file_path = os.path.join(self.root, AVATAR_PATH, av)
                self._download_image(url, file_path)

    def fetch_room_icons(self):
        for room_id in self.room_dat:
            if 'ic' in self.room_dat[room_id]:
                ic = self.room_dat[room_id]['ic']
                if not isinstance(ic, str):
                    continue
                url = ICON_BASE_URL + ic
                file_path = os.path.join(self.root, ICON_PATH, ic)
                self._download_image(url, file_path)

    def _download_image(self, url, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        res = requests.get(url, stream=True)
        if res.status_code == 200:
            with open(file_path, 'wb') as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)

    def _init_load(self):
        '''
        request 'init_load' command to load Chatworks settings
        '''
        param = {
           'cmd': 'init_load',
           'myid': self.myid,
           '_v': '1.80a',
           '_av': '5',
           '_t': self.token,
           'ln': 'ja',
           'rid': '0',
           'type': '',
           'new': '1',
        }
        res = self._get_from_gateway(param)

        status = res.json()['status']['success']
        if not status:
            raise ValueError('status')
        self.config = res.json()['result']

        with open(os.path.join(self.root, ACCOUNT_CONFIG_FILE), 'w') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def _load_old_chat(self, room_id, first_chat_id=0):
        '''
        request 'load_old_chat' command to get old chats on room
        '''
        param = {
           'cmd': 'load_old_chat',
           'myid': self.myid,
           '_v': '1.80a',
           '_av': '5',
           '_t': self.token,
           'ln': 'ja',
           'room_id': str(room_id),
           'last_chat_id': '0',
           'first_chat_id': str(first_chat_id),
           'jump_to_chat_id': '0',
           'unread_num': '0',
           'file': '1',
           'desc': '1',
        }
        res = self._get_from_gateway(param)

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
        param = {
           'cmd': 'download_file',
           'bin': '1',
           'file_id': str(file_id),
        }
        res = self._get_from_gateway(param)

        if 'Content-disposition' not in res.headers:
            # TODO must logging!
            print('Missing "Content-disposition" header: ' + str(file_id))
            return
        filename = self._dig_up_filename(res.headers['Content-disposition'])

        output_dir = os.path.join(self.root, FILE_PATH, str(file_id))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        fpath = os.path.join(output_dir, filename)
        with open(fpath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=128):
                f.write(chunk)

    def _download_preview(self, file_id):
        param = {
           'cmd': 'preview_file',
           'bin': '1',
           'file_id': str(file_id),
        }
        res = self._get_from_gateway(param)

        if 'Content-disposition' not in res.headers:
            # TODO must logging!
            print('None Content-disposition headers: ' + str(file_id))
            return
        filename = self._dig_up_filename(res.headers['Content-disposition'])

        output_dir = os.path.join(self.root, THUMB_PATH, str(file_id))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        fpath = os.path.join(output_dir, filename)
        with open(fpath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=128):
                f.write(chunk)

    def _dig_up_filename(self, contents):
        filename_all = re.findall(r"attachment;filename\*=UTF-8''(.+)",
                                  contents)
        filename_old_all = re.findall(r"filename=\"=\?UTF-8\?B\?(.+)\?=\"",
                                      contents)
        if len(filename_all) > 0:
            filename = urllib.parse.unquote(filename_all[0])
        elif len(filename_old_all) > 0:
            filename = base64.b64decode(filename_old_all[0])
        else:
            raise Exception(contents)
        # if filename is instance of bytes
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        elif not isinstance(filename, str):
            raise Exception(filename)
        return filename

    def _get_from_gateway(self, param):
        '''
        req gateway
        '''
        cnt = 0
        while cnt < MAX_RETRY_CNT:
            try:
                param_list = []
                for key in param:
                    param_list.append(key + '=' + str(param[key]))

                query = '&'.join(param_list)
                res = self.session.get(GATEWAY_URL + '?' + query,
                                       timeout=(5, 10 * 60))
                break
            except (ConnectionError, ReadTimeout) as e:
                print('raised: ' + e.__class__.__name__ + ' , cnt:' + str(cnt))
                # count up
                cnt += 1
                if cnt >= MAX_RETRY_CNT:
                    # TODO logging retry over
                    print('wait for forgived')
                    self._wait_till_forgived()
                    cnt = 0
                else:
                    self._wait_interval()
        return res

    def _wait_interval(self):
        ''' wait a little (a few seconds, and so on) '''
        time.sleep(INTERVAL_ORDER * random.uniform(1.0, 4.0))

    def _wait_till_forgived(self):
        ''' wait long (some minites or an hour, and so on) '''
        time.sleep(LONG_INTERVAL_ORDER * random.uniform(1.0, 2.0))

    @property
    def contact_dat(self):
        ''' contact json string '''
        return self.config['contact_dat']

    @property
    def room_dat(self):
        ''' room json string '''
        return self.config['room_dat']
