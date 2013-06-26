import __init__ as modules

class LoggerModule(modules.Module):
  hooks = [('pubcmd', 'log')]

  def __init__(self, config):
    self.config = config
    self.logfile = open(self.config.logger_logfile, "a")

  def log(self, message):
    timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
    self.logfile.write('%s %s\n' % (timestamp, message))
    self.logfile.flush()

  def pubcmd(self, source, message):
    self.log(source + ' ' + message)

  def close(self):
    self.logfile.close()

Module = LoggerModule
