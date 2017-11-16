# -*- coding:utf-8 -*-

from ..const import *

import os
import json


class ChatStorage(object):
    def __init__(self, path):
        self._myid = None
        self._chat_offsets = {}
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

    def get_next_offset(self, room_id=None, offset=None):
        room_offsets = self._get_room_offsets(room_id)
        if len(room_offsets) == 0:
            # room_offsets == [] -> '(room_id)_last.json' only
            return None
        elif not offset:
            # offset is None -> last offset
            return self._chat_offsets[str(room_id)][-1]
        room_offsets = self._chat_offsets[str(room_id)]
        if int(offset) not in room_offsets:
            return None
        current = room_offsets.index(int(offset))
        if current == 0:
            return None
        return room_offsets[current - 1]

    def get_prev_offset(self, room_id=None, offset=None):
        room_offsets = self._get_room_offsets(room_id)
        if len(room_offsets) == 0:
            # room_offsets == [] -> '(room_id)_last.json' only
            return None
        elif not offset:
            # offset is None -> last offset
            return None
        room_offsets = self._chat_offsets[str(room_id)]
        if int(offset) not in room_offsets:
            return None
        current = room_offsets.index(int(offset))
        if current == len(room_offsets) - 1:
            return None
        return room_offsets[current + 1]

    def _get_room_offsets(self, room_id):
        if room_id not in self._chat_offsets:
            offset_list = []
            files = os.listdir(os.path.join(self.root, room_id))
            for fname in files:
                if not fname:
                    continue
                # 12345_xxxxxxxxxx.json -> xxxxxxxxxx
                tmp_offset = fname[len(str(room_id)) + 1:-5]
                if tmp_offset.isdigit():
                    offset_list.append(int(tmp_offset))
            self._chat_offsets[str(room_id)] = sorted(offset_list)
        return self._chat_offsets[str(room_id)]
