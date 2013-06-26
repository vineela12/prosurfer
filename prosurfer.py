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
    map(self._register_module, self.factory.config.mods.split(','))

    self.nickname = self.factory.config.nickname
    self.channel = self.factory.config.channel

    irc.IRCClient.connectionMade(self)

  def connectionLost(self, reason):
    irc.IRCClient.connectionLost(self, reason)

  def signedOn(self):
    self.join(self.channel)

  def on_pubmsg(self, conn, event):
    message = event.arguments[0]
    # if it's a 'command'
    if message.startswith(self.factory.config.prompt):
      prompt_length = len(self.factory.config.prompt)
      command = message[prompt_length:message.find(' ', prompt_length)]

      self.hooks['pubcmd'][command](event.source, message[prompt_length+len(command):])
    else:
      map(lambda hook: hook(event), self.hooks['pubmsg'])

  def _register_module(self, module):
    self.register_module(import_module('modules.' + module), self.factory.config)

  def register_module(self, module, config):
    md = module.Module(config)
    simple_hooks = filter(lambda hook: type(hook) == str, md.hooks)
    args_hooks = filter(lambda hook: type(hook) == tuple, md.hooks)

    for hook in simple_hooks:
      self.hooks[hook].append(getattr(md, hook))
    for hook in args_hooks:
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
