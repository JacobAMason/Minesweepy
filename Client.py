# coding=utf-8
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from Minesweeper_tdd import Game

__author__ = 'JacobAMason'




class Bot(irc.IRCClient):
    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    @property
    def nickname(self):
        return self.factory.nickname

    def joined(self, channel):
        print "Joined %s." % (channel,)
        self.say(channel, "Hello, %s!" % (channel))

    def command(self, user, message):
        if message == "help":
            self.msg(user, "Say 'start' to start a game.")
        elif message == "start":
            self.game = Game(3, 3, 2)
            self.msg(user, self.game.show_welcome_message())
            self.msg(user, self.game.show_board())


    def privmsg(self, user, channel, message):
        user = user.split("!", 1)[0]
        if channel == self.nickname:
            self.command(user, message)

    def dataReceived(self, bytes):
        print str(bytes).rstrip()
        # Make sure to up-call - otherwise all of the IRC logic is disabled!
        return irc.IRCClient.dataReceived(self, bytes)


class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason)

if __name__ == "__main__":
    host = "irc.freenode.net"
    port = 6667
    chan = "msstate"
    reactor.connectTCP(host, port, BotFactory("#" + chan, nickname="Minesweepy"))
    reactor.run()