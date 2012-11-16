from tornado import websocket
from server.Game import GamesRepo

class DisplayWebSocketHandler(websocket.WebSocketHandler):

    #noinspection PyMethodOverriding
    def open(self, gameId):
        self.game = GamesRepo.instance()[gameId]
        self.game.addDisplay(self)
        print 'display initialized with gameId', gameId

    def on_message(self, message):

        self.game.handleMessageFromDisplay(message)
        print "Display said: %s" % (message)
