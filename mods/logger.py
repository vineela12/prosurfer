import __init__ as mods

class LoggerMod(mods.Mod):
  hooks = [('pubcmd', 'log')]

  def log(self, message):
    with file(self.config.logger_logfile, 'a') as logfile:
      logfile.write(message)

  def pubcmd(self, sender, message):
    self.log(sender + ' ' + message + '\n')

Mod = LoggerMod
