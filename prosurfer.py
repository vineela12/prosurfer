import sys

from ConfigParser import ConfigParser
from importlib import import_module

import irc.bot

from util import Struct
import mods

default_config = {
    'nickname': 'prosurfer',
    'channel' : '#lean-bots',
    'server' : 'irc.oftc.net',
    'port' : '6667',
    'nickname' : 'prosurfer',
    'username' : 'ProSurfer 4.3',
    'prompt' : '`',
    'mods' : '',
    }

class ProSurfer(irc.bot.SingleServerIRCBot):
  def __init__(self, config):
    """
    Read a configuration file and start the bot.
    """

    self.config = Struct(config)

    hooks = ['pubmsg', 'privmsg', 'join', 'part', 'topic', 'chanmode']
    self.hooks = dict(map(lambda hook: (hook, []), hooks))
    self.hooks['pubcmd'] = {}
    # create a dict of hook-type => [hooks]
    # 
    # each hook in the hooks list will be called with data when a hook-type
    # message is received.

    super(ProSurfer, self).__init__(
        [(self.config.server, int(self.config.port))],
        self.config.nickname, self.config.username)

    # Register all the mods
    map(self._register_mod, self.config.mods.split(','))

    self.channel = self.config.channel

  def on_welcome(self, conn, event):
    conn.join(self.channel)

  def on_pubmsg(self, conn, event):
    message = event.arguments[0]
    # if it's a 'command'
    if message.startswith(self.config.prompt):
      prompt_length = len(self.config.prompt)
      command = message[prompt_length:message.find(' ', prompt_length)]

      self.hooks['pubcmd'][command]('sender', message[prompt_length+len(command):])
    else:
      map(lambda hook: hook(event), self.hooks['pubmsg'])

  def _register_mod(self, mod):
    self.register_mod(import_module('mods.' + mod), self.config)

  def register_mod(self, mod, config):
    md = mod.Mod(config)
    simple_hooks = filter(lambda hook: type(hook) == str, md.hooks)
    args_hooks = filter(lambda hook: type(hook) == tuple, md.hooks)

    for hook in simple_hooks:
      self.hooks[hook].append(getattr(md, hook))
    for hook in args_hooks:
      self.hooks[hook[0]][hook[1]] = getattr(md, hook[0])

