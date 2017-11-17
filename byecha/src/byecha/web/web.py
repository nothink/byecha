# -*- coding:utf-8 -*-

from .handler import WebHandler, FileHandler
from .storage import ChatStorage
from ..const import *

import os
from multiprocessing import Process

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application


class WebProcess(Process):
    '''
    HTTP server process class
    '''
    def __init__(self,
                 port, address='0.0.0.0',
                 path='./dump', proc_num=0, debug=False):
        '''
        initializer
        '''
        super().__init__()

        self.port = port
        self.address = address
        self.proc_num = proc_num
        self.debug = debug

        self.storage = ChatStorage(path)
        self.root = path

    def run(self):
        '''
        run process
        '''
        app = Application(
            [
                (r'/file/([0-9]+)',
                 FileHandler, dict(root=self.root, mode='file')),
                (r'/thumb/([0-9]+)',
                 FileHandler, dict(root=self.root, mode='thumb')),
                (r'.*', WebHandler, dict(storage=self.storage)),
            ],
            template_path=os.path.join(self.root, TEMPLATE_PATH),
            static_path=self.root,
            debug=self.debug)
        server = HTTPServer(app)

        print('binding ' + self.address + '@' + str(self.port))
        server.bind(self.port, address=self.address)
        print('http server is up ...')
        server.start(self.proc_num)

        IOLoop.instance().start()

    def join(self, timeout=None):
        '''
        join process
        '''
        super().join(timeout)
