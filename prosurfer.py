from ConfigParser import ConfigParser
from importlib import import_module

import irc.bot

import mods

default_config = {
    'nickname': 'prosurfer',
    'channel' : '#lean-bots',
    'server' : 'irc.oftc.net',
    'port' : '6667',
    'nickname' : 'prosurfer',
    'username' : 'ProSurfer 4.3'
    }

class ProSurfer(irc.bot.SingleServerIRCBot):
  def __init__(self, config):
    self.config = ConfigParser(default_config)
    self.config.read(config)
    self.hooks = { 'pubmsg': [], 'privmsg': [], 'join': [], 'part': [],
        'topic': [], 'chanmode': [], }

    irc.bot.SingleServerIRCBot.__init__(self,
        [(self.config.get('DEFAULT', 'server'), int(self.config.get('DEFAULT', 'port')))],
        self.config.get('DEFAULT', 'nickname'), self.config.get('DEFAULT', 'username'))

    map(self._register_mod, self.config.get('DEFAULT', 'mods').split(','))

    self.channel = self.config.get('DEFAULT', 'channel')

  def on_welcome(self, conn, event):
    conn.join(self.channel)

  def on_pubmsg(self, conn, event):
    map(lambda hook: hook(event), self.hooks['pubmsg'])

  def _register_mod(self, mod):
    self.register_mod(import_module('mods.' + mod), dict(self.config.items(mod)))

  def register_mod(self, mod, config):
    md = mod.Mod(config)
    map(lambda hook: self.hooks[hook].append(getattr(md, hook)), md.hooks)

if __name__ == '__main__':
  bot = ProSurfer('.prosurferrc')
  bot.start()
