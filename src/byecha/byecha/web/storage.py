# -*- coding:utf-8 -*-

from ..const import *

import json


class ChatStorage(object):
    def __init__(self, path):
        self.root = path

    @property
    def chat_list(self):
        pass
