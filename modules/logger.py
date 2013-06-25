import __init__ as modules

class LoggerModule(modules.Module):
  hooks = [('pubcmd', 'log')]

  def log(self, message):
    with file(self.config.logger_logfile, 'a') as logfile:
      logfile.write(message)

  def pubcmd(self, source, message):
    self.log(source + ' ' + message + '\n')

Module = LoggerModule
