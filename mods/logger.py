import __init__ as mods

class LoggerMod(mods.Mod):
  hooks = ['pubmsg']

  def log(self, message):
    with file(self.config['logfile'], 'a') as logfile:
      logfile.write(message)

  def pubmsg(self, event):
    if(event.arguments[0].startswith('`log ')):
      self.log(event.source + ' ' + event.arguments[0][5:] + '\n')

Mod = LoggerMod
