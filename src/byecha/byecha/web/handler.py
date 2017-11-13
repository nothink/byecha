# -*- coding:utf-8 -*-

from tornado.web import RequestHandler, asynchronous

import json


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
        chat_list = json.load(
            open('/Users/kaba/Projects/ByeCha/src/byecha/_dump/json/111250/111250_last.json'))
        room_list = json.load(
            open('/Users/kaba/Projects/ByeCha/src/byecha/_dump/json/room_dat.json'))
        contact_list = json.load(
            open('/Users/kaba/Projects/ByeCha/src/byecha/_dump/json/contact_dat.json'))
        self.render("index.html",
                    chat_list=chat_list,
                    room_list=room_list,
                    contact_list=contact_list)

    post = get
