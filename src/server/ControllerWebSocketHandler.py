from tornado import websocket
from server.Game import GamesRepo


class ControllerWebSocketHandler(websocket.WebSocketHandler):

    #noinspection PyMethodOverriding
    def open(self, gameId, controllerId):
        print 'controller got gameId', gameId, 'and controllerId', controllerId
        self.game = GamesRepo.instance()[gameId]
        self.controllerId = controllerId
        self.game.addController(self)


    def on_message(self, message):
        self.game.handleMessageFromController(self.controllerId, message)
        print "Controller %s said: %s" % (self.controllerId, message)
