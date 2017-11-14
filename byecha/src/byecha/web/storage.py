# -*- coding:utf-8 -*-

from ..const import *

import os
import json


class ChatStorage(object):
    def __init__(self, path):
        self._myid = None
        if os.path.isdir(path):
            self.root = path
        else:
            raise FileNotFoundError(path)

    def get_chat_list(self, room_id=None, offset=None):
        if not room_id:
            return None
        room_id = room_id if room_id else ''
        chat_tail = str(offset) if offset else 'last'
        chat_filename = str(room_id) + '_' + chat_tail + '.json'
        chat_path = os.path.join(self.root, room_id, chat_filename)
        return json.load(open(chat_path))

    @property
    def myid(self):
        if not self._myid:
            with open(os.path.join(self.root, MYID_FILE)) as f:
                self._myid = f.read().strip()
        return self._myid

    @property
    def room_list(self):
        return self.config['room_dat']

    @property
    def contact_list(self):
        return self.config['contact_dat']

    @property
    def config(self):
        ''' get user's all config dictionary '''
        return json.load(open(os.path.join(self.root, ACCOUNT_CONFIG_FILE)))
