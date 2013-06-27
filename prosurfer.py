import sys

from importlib import import_module

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from util import Struct
from config import config

import modules

class ProSurfer(irc.IRCClient):
    def __init__(self):
        self.hooks = {
            'pubcmd'   : {},
            'pubmsg'   : [],
            'privmsg'  : [],
            'join'     : [],
            'part'     : [],
            'topic'    : [],
            'chanmode' : [],
        }

    def connectionMade(self):
        map(self.__registerModule, self.factory.config.mods.split(','))

        self.nickname = self.factory.config.nickname
        self.channel = self.factory.config.channel

        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        self.join(self.channel)

    def on_pubmsg(self, conn, event):
        message = event.arguments[0]
        prompt = self.factory.config.prompt
        # if it's a 'command'
        if message.startswith():
            promptLength = len(prompt)
            command = message[promptLength:message.find(' ', promptLength)]

            self.hooks['pubcmd'][command](event.source, message[promptLength + len(command):])
        else:
            map(lambda hook: hook(event), self.hooks['pubmsg'])

    def __registerModule(self, module):
        self.registerModule(import_module('modules.' + module), self.factory.config)

    def registerModule(self, module, config):
        md = module.Module(config)
        simpleHooks = filter(lambda hook: type(hook) == str, md.hooks)
        argsHooks = filter(lambda hook: type(hook) == tuple, md.hooks)

        for hook in simpleHooks:
            self.hooks[hook].append(getattr(md, hook))
        for hook in argsHooks:
            self.hooks[hook[0]][hook[1]] = getattr(md, hook[0])

class ProSurferFactory(protocol.ClientFactory):
    """
    A factory for prosurfers.
    A new protocol instance will be created each time we connect to the server.
    """
    def __init__(self, config):
        self.config = config

    def buildProtocol(self, addr):
        prosurfer = ProSurfer()
        prosurfer.factory = self
        return prosurfer

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == "__main__":
    config = Struct(config)
    p = ProSurferFactory(config)
    reactor.connectTCP(config.server, 6667, p)
    reactor.run()
