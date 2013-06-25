import sys

from ConfigParser import ConfigParser
from importlib import import_module

import irc.bot

from util import Struct
import modules

class ProSurfer(irc.bot.SingleServerIRCBot):
  def __init__(self, config):

    self.config = Struct(config) 
    self.hooks = {
      'pubcmd'   : {},
      'pubmsg'   : [],
      'privmsg'  : [],
      'join'     : [],
      'part'     : [],
      'topic'    : [],
      'chanmode' : [],
    }

    super(ProSurfer, self).__init__(
        [(self.config.server, int(self.config.port))],
        self.config.nickname, self.config.username)

    map(self._register_module, self.config.mods.split(','))

    self.channel = self.config.channel

  def on_welcome(self, conn, event):
    conn.join(self.channel)

  def on_pubmsg(self, conn, event):
    message = event.arguments[0]
    # if it's a 'command'
    if message.startswith(self.config.prompt):
      prompt_length = len(self.config.prompt)
      command = message[prompt_length:message.find(' ', prompt_length)]

      self.hooks['pubcmd'][command](event.source, message[prompt_length+len(command):])
    else:
      map(lambda hook: hook(event), self.hooks['pubmsg'])

  def _register_module(self, module):
    self.register_module(import_module('modules.' + module), self.config)

  def register_module(self, module, config):
    md = module.Module(config)
    simple_hooks = filter(lambda hook: type(hook) == str, md.hooks)
    args_hooks = filter(lambda hook: type(hook) == tuple, md.hooks)

    for hook in simple_hooks:
      self.hooks[hook].append(getattr(md, hook))
    for hook in args_hooks:
      self.hooks[hook[0]][hook[1]] = getattr(md, hook[0])

