# -*- coding:utf-8 -*-

from ..const import *

import os
from urllib.parse import urlparse, quote
from mimetypes import guess_type

from tornado.web import RequestHandler, asynchronous


class WebHandler(RequestHandler):
    '''
    HTTP Handler Class
    '''
    SUPPORTED_METHODS = ("GET", "POST")

    def initialize(self, storage):
        '''
        initializer
        '''
        self.storage = storage

    @asynchronous
    def get(self):
        '''
        async GET method handling method
        '''
        uri = urlparse(self.request.uri)
        dirs = uri.path.split("/")
        room_id = dirs[1] if len(dirs) > 1 else None
        offset = dirs[2] if len(dirs) > 2 else None

        self.render("index.html",
                    myid=self.storage.myid,
                    room_id=room_id,
                    offset=offset,
                    prev_offset=self.storage.get_prev_offset(room_id, offset),
                    next_offset=self.storage.get_next_offset(room_id, offset),
                    chat_list=self.storage.get_chat_list(room_id, offset),
                    room_list=self.storage.room_list,
                    contact_list=self.storage.contact_list)

    post = get


class FileHandler(RequestHandler):
    '''
    HTTP Handler Class for file downloading
    '''
    SUPPORTED_METHODS = ("GET")

    def initialize(self, root, mode):
        '''
        initializer
        '''
        self.root = root
        self.mode = mode

    @asynchronous
    def get(self, file_id):
        '''
        async GET method handling method
        '''
        def get_file_path(file_id):
            if self.mode == 'file':
                dirname = FILE_PATH
            elif self.mode == 'thumb':
                dirname = THUMB_PATH
            else:
                raise AttributeError(self.mode)
            dir_path = os.path.join(self.root, dirname, str(file_id))
            files = os.listdir(dir_path)
            if len(files) != 1:
                raise FileNotFoundError(file_id)
            return (files[0], os.path.join(dir_path, files[0]))

        filename, filepath = get_file_path(file_id)
        mime = guess_type(filepath)
        self.set_header('Content-Type', mime[0])
        self.set_header('Content-Length', os.path.getsize(filepath))
        if self.mode == 'file':
            self.set_header('Content-disposition',
                            'attachment;filename*=UTF-8\'\'' + quote(filename))

        with open(filepath, 'rb') as f:
            self.write(f.read())
        self.finish()
