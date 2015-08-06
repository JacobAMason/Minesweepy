# coding=utf-8
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from Minesweeper_tdd import Game

__author__ = 'JacobAMason'

class GameStateMachine:
    clients = {}

    def __init__(self, user):
        self.user = user
        self.clients[user] = self
        self.state_callback = self.welcome_instructions
        self.game = Game()
        self.respond("start")

    def msg(self, message):
        raise NotImplementedError

    def error(self, message):
        self.msg("I don't know what you mean by '%s'" % message)

    def welcome_instructions(self, message):
        self.msg(self.game.show_welcome_message())
        self.state_callback = self.pick_board_size

    def pick_board_size(self, message):
        if len(message) == 1 and message[0].isdigit() and int(
                message[0]) in [1, 2, 3]:
            self.setup_board(int(message[0]))
            self.state_callback = self.game_loop
            self.msg(self.game.show_board())
        else:
            self.error(message)

    def setup_board(self, size):
        if size == 1:
            self.game.generate_board(5, 5, 3)
        elif size == 2:
            self.game.generate_board(10, 5, 6)
        elif size == 3:
            self.game.generate_board(15, 5, 9)

    def game_loop(self, message):
        self.game.process_input(message)

        errors = list(self.game.show_errors())
        if len(errors) > 0:
            map(self.msg, errors)
        else:
            self.msg(self.game.show_board())

        if self.game.board.check_end_game_win() \
                or self.game.board.check_end_game_loss():
            self.clients.pop(self.user)

    def respond(self, message):
        self.state_callback(message)

class Bot(irc.IRCClient):

    class IRCStateMachine(GameStateMachine):
        def __init__(self, user, botInstance):
            self.bot = botInstance
            GameStateMachine.__init__(self, user)

        def msg(self, message):
            self.bot.msg(self.user, message)

    def privmsg(self, user, channel, message):
        user = user.split("!", 1)[0]
        if channel == self.nickname:
            self.command(user, message)
        elif message == "help":
            self.say(channel, "Send 'start' to me in a direct message.")

    def command(self, user, message):
        if message == "help":
            self.msg(user, "Say 'start' to start a game.")
        elif self.IRCStateMachine.clients.has_key(user):
            self.IRCStateMachine.clients[user].respond(message)
        elif message == "start":
            self.IRCStateMachine(user, self)
        else:
            self.msg(user, "*wat*\nSay 'help' to figure this thing out.")

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    @property
    def nickname(self):
        return self.factory.nickname

    def userJoined(self, user, channel):
        user = user.split("!", 1)[0]
        self.msg(user, "Say 'start' to start a game.")

    def joined(self, channel):
        print "Joined %s." % (channel,)
        self.say(channel, (
                     "Hello, %s !\n"
                     "Start a direct message with me to play." % (channel))
                 )

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
    host = "coop.test.adtran.com"
    port = 6667
    chan = "Minesweepy"
    reactor.connectTCP(host, port,
                       BotFactory("#" + chan, nickname="Minesweepy"))
    reactor.run()
