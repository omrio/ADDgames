#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import sys

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tornado
from DisplayWebSocketHandler import DisplayWebSocketHandler
from ControllerWebSocketHandler import ControllerWebSocketHandler

def main():
    application = tornado.web.Application([
        (r"/(?P<gameId>[0-9a-fA-F\-]+)/display", DisplayWebSocketHandler),
        (r"/(?P<gameId>[0-9a-fA-F\-]+)/controller/(?P<controllerId>[0-9a-fA-F\-]+)", ControllerWebSocketHandler),
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()