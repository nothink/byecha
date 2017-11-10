# -*- coding:utf-8 -*-

from .handler import WebHandler

import os
from multiprocessing import Process

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application


class WebProcess(Process):
    def __init__(self, port, address='0.0.0.0', proc_num=0, debug=False):
        super().__init__()

        self.port = port
        self.address = address
        self.proc_num = proc_num
        self.debug = debug

    def run(self):
        app = Application([(r"/", WebHandler), ],
                          template_path=os.path.join(os.getcwd(),  "static/templates"),
                          static_path=os.path.join(os.getcwd(),  "static"),
                          debug=self.debug)
        server = HTTPServer(app)

        print('binding ' + self.address + '@' + str(self.port))
        server.bind(self.port, address=self.address)
        print('http server is up ...')
        server.start(self.proc_num)

        IOLoop.instance().start()

    def join(self, timeout=None):
        super().join(timeout)
