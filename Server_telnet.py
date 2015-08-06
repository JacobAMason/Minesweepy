#!python
__author__ = 'JacobAMason'

from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import StatefulTelnetProtocol
from twisted.internet import reactor

from time import sleep
class ShellTelnet():
    def __init__(self):
       pass

class TelnetServerProtocol(StatefulTelnetProtocol):
    def connectionMade(self):
        print "DEBUG: connectionMade called"
        banner = [
"   ____    ____  _                                                          ",
"  |_   \  /   _|(_)                                                         ",
"    |   \/   |  __  _ .--. .---. .--. _   _   __ .---. .---. _ .--.  _   __ ",
"    | |\  /| | [  |[ `.-. / /__\( (`\[ \ [ \ [  / /__\/ /__\[ '/'`\ [ \ [  ]",
"   _| |_\/_| |_ | | | | | | \__.,`'.'.\ \/\ \/ /| \__.| \__.,| \__/ |\ '/ / ",
"  |_____||_____[___[___||__'.__.[\__) )\__/\__/  '.__.''.__.'| ;.__[\_:  /  ",
"                                                            [__|    \__.'   "
        ]

        for line in banner:
            self.sendLine(line + "\r")

    def lineReceived(self, line):
        line = line.strip()
        print "DEBUG: lineReceived called with %s" % line
        if line != "exit":
            self.sendLine("Echo: " + line + "\r")
        else:
            self.sendLine("Bye")
            self.transport.loseConnection()
        self.clearLineBuffer()

    def connectionLost(self, reason):
        print "DEBUG: connectionLost called with: %s" % str(reason)

def TelnetServerFactory():
    factory = ServerFactory()
    factory.protocol = TelnetServerProtocol
    return factory

if __name__ == "__main__":
    protocol = TelnetServerFactory()
    reactor.listenTCP(23, protocol)
    reactor.run()