# -*- coding:utf-8 -*-

from tornado.web import RequestHandler, asynchronous

from urllib.parse import urlparse


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
                    chat_list=self.storage.get_chat_list(room_id, offset),
                    room_list=self.storage.room_list,
                    contact_list=self.storage.contact_list)

    post = get
