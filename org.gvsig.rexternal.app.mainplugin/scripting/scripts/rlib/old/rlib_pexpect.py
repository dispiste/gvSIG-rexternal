
from gvsig import *

import pexpect
import StringIO
import re
from java.io import File
from org.gvsig.andami import PluginsLocator

from rlib_base import REngine_base


def toRAsString(value):
  if isinstance(value,str) or isinstance(value,unicode) :
    return '"' + repr(value)[1:-1] + '"'
  return str(value)

def debug(type, *values):
  #return
  print "::%-7.7s:" % type,
  for value in values:
    print value,
  print

class _ProxyFunction(object):
  def __init__(self, R, name):
    self._R = R
    self._name = name

  def __call__(self,*args):
    cmd = StringIO.StringIO()
    cmd.write(self._name)
    cmd.write("(")
    n = 0
    for arg in args:
      if n>0 and n<len(args):
        cmd.write(", ")
      cmd.write(toRAsString(arg))
      n+=1
    cmd.write(")")
    cmd = cmd.getvalue()
    x = self._R.eval(cmd)
    debug("CALLFN", repr(x))
    return x

RE_ERROR = re.compile("Error[^:]*:")

def getRExecPathname():
  manager = PluginsLocator.getManager()
  plugin = manager.getPlugin("org.gvsig.r.app.mainplugin")
  return File(plugin.getPluginDirectory(),"R/bin/x64/R.exe")

class REngine_pexpect(REngine_base):
  def __init__(self, consoleListener=None):
    REngine_base.__init__(self,consoleListener)
    
    self._collectors = list()
    self._skip = list()
    self._prompt="@xx@>"
    rexec = self.getPathName(getRExecPathname())
    debug("REXEC",rexec)
    self._R = pexpect.spawn(rexec,logfile=self)
    #self._R.setecho(False)
    #self._R.expect(">")
    self._R.sendline('options(prompt="%s", continue=" ")' % self._prompt)
    self._R.expect(self._prompt)

  def flush(self):
    pass

  def write(self,s):
    if s.endswith(self._prompt):
      debug("PROMPT", repr(s))
      s = s[:-len(self._prompt)]
      if s.strip()=="":
        debug("EMPTY", repr(s))
        return
      n1 = s.rfind("[1] ")
      n2 = s.rfind("\n")
      debug("ADDNL1", n1, n2, repr(s))
      debug("ADDNL2", n1>=0, n1 > n2, s[n1-1]!="\n", repr(s[n1-1]))
      if( n1>=0 and n1 > n2 and s[n1-1]!="\n"):
        s = s[:n1]+"\r\n"+s[n1:]
    if "\r\n" in s:
      debug("SPLIT", repr(s))
      n=1
      lines = s.split("\r\n")
      for line in lines:
        if not(n==len(lines) and line==""):
          self.write2(line+"\r\n")
        n+=1
      return
    self.write2(s)

  def write2(self,s):
    if len(self._skip)>0 and s == self._skip[-1] :
      debug("SKIP", repr(s))
      self._skip.pop()
      return
    if s.startswith("[1] ") :
      s = s[4:]
      debug("COLLECT", repr(s))
      for collector in self._collectors:
        collector.append(s)
    elif RE_ERROR.match(s):
      debug("COLLECT", repr(s))
      for collector in self._collectors:
        collector.append(s)
      self.console_output(s,1)
    else:
      self.console_output(s,0)

  def writelines(self, lines):
    for line in lines:
      self.write(line)
      self.write("\n")

  def isatty(self):
    return False

  def close(self):
    pass

  def getclass(self,name):
    cmd = 'class(%s)' % name
    self.addCollector()
    self._skip.append("\n")
    self._skip.append(cmd)
    self._R.sendline(cmd)
    self._R.expect(self._prompt)
    x = self.popCollector()
    x = x[0].strip()
    if x[0] == '"':
      x = x[1:-1]
    if x.startswith("Error:"):
      raise AttributeError(x[6:])
    debug("CLASS", name, " RETURN ",repr(x))
    return x

  def _eval(self,expresion):
    self.addCollector()
    self._skip.append("\n")
    self._skip.append(expresion)
    self._R.sendline(expresion)
    self._R.expect(self._prompt)
    x = self.popCollector()
    # popCollector return a list of String
    # get the last item
    if len(x) > 0:
      x = x[-1].strip()
    else:
      x = None
    debug("_EVAL", expresion, " COLLECT",repr(x))
    return x

  def eval(self,expresion):
    x = self._eval(expresion)
    if not x in (None, ""):
      if x[0] == '"':
        x = x[1:-1]
      else:
        try:
          x = int(x)
        except:
          try:
            x = float(x)
          except ValueError:
            pass
    debug("EVAL", expresion, " RETURN ",repr(x))
    return x

  def addCollector(self, collector=None):
    if collector == None:
      collector = list()
    self._collectors.append(collector)
    return collector

  def popCollector(self):
    collector = self._collectors.pop()
    return collector

  def __setattr__(self,name,value):
    if name in ("_R", "_consoleListeners",
      "_collectors", "_prompt", "_skip" ):
      self.__dict__[name] = value
    else:
      s = '%s <- %s' % (name,toRAsString(value))
      self._eval(s)

  def __getattr__(self,name):
    class_ = self.getclass(name)
    if class_ == "function":
      return _ProxyFunction(self,name)
    else:
      return self.eval(name)

  def source(self,pathname):
    getAbsolutePath = getattr(pathname,"getAbsolutePath", None)
    if getAbsolutePath != None:
        pathname = getAbsolutePath()
    pathname = pathname.replace("\\","/")
    x = self._eval('source("%s")' % pathname)
    debug("SOURCE",repr(x))
    if x!=None and RE_ERROR.match(x):
      raise Exception(x)

  def end(self):
    self._consoleListeners = list()
    self._R.close()
  
def getREngine(consoleListener=None):
    return REngine_pexpect(consoleListener)

def main(*args):
  R = getREngine()
  R.end()
  import sys
  print "platform:",sys.platform
  
  