from collections import defaultdict
from utils.singleton import Singleton

class GamesRepo(Singleton, defaultdict):

    def __init__(self):
#        super(defaultdict, self).__init__(default_factory = lambda : Game())
        self.default_factory = lambda : Game()


def parseMessageWithAddressee(messageWithAddressee):
    """
    The addressee is a controllerId, the rest of the message is the content
    Message format: "<controllerId> <content>" (without the quotes)
    """
    addressee, content = messageWithAddressee.split(' ', 1)
    return addressee, content

def formatMessageWithControllerId(controllerId, content):
    """
    Message format: "<controllerId> <content>" (without the quotes)
    """
    messageWithControllerId = '%s %s' % (controllerId, content)
    return messageWithControllerId


class Game(object):

    def __init__(self):

        self.displays = []
        self.controllers = {}


    def addController(self, controller):
        if controller.controllerId not in self.controllers:
            self.controllers[controller.controllerId] = controller
        else:
            print 'Controller', controller.controllerId, 'already added to this game'


    def removeController(self, controllerId):
        if controllerId in self.controllers:
            del self.controllers[controllerId]
        else:
            print 'Controller', controllerId, 'was never added to this game'


    def addDisplay(self, display):
        if display not in self.displays:
            self.displays.append(display)
        else:
            print 'Display', display, 'already added to this game'


    def removeDisplay(self, display):
        if display in self.displays:
            self.displays.remove(display)
        else:
            print 'Display', display, 'was never added to this game'


    def handleMessageFromController(self, controllerId, message):
        messageWithControllerId = formatMessageWithControllerId(controllerId, message)
        for display in self.displays:
            display.write_message(messageWithControllerId)


    def handleMessageFromDisplay(self, messageWithAddressee):
        addressee, content = parseMessageWithAddressee(messageWithAddressee)
        if addressee not in self.controllers:
            print 'Controller', addressee, 'not in this game'
        else:
            self.controllers[addressee].write_message(content)
