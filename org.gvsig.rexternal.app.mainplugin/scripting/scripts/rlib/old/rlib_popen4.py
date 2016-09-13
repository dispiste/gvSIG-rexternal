
import subprocess
import thread
import threading
import StringIO
import re
from org.gvsig.tools import ToolsLocator

import rlib_base
reload(rlib_base)

RE_ERROR = re.compile("Error[^:]*:")
 


def debug(otype, *values):
  #return
  print "::%-7.7s:" % otype,
  for value in values:
    print value,
  print


class RValue:
  def __init__(self, value):
    self._value = value

  def __str__(self):
    s = self._value
    if s==None:
      return "None"
    if s.startswith("[1] "):
      s = s[4:].strip()
    if s[0]=='"':
      s = s[1:-1]
    return s

  def __repr__(self):
    return repr(str(self))

  def __int__(self):
    return int(str(self))

  def __long__(self):
    return long(str(self))

  def __float__(self):
    return float(str(self))

  def asint(self):
    return int(str(self))

  def asstr(self):
    return str(self)

  def asfloat(self):
    return float(str(self))

  def aslist(self):
    return None

class RFunction:
  def __init__(self,rengine,funcname):
    self._rengine = rengine
    self._funcname = funcname

  def __call__(self,*args):
    cmd = StringIO.StringIO()
    cmd.write(self._funcname)
    cmd.write("(")
    n = 0
    for arg in args:
      if n>0 and n<len(args):
        cmd.write(", ")
        if isinstance(arg,str) or isinstance(arg,unicode) :
          arg = '"' + repr(arg)[1:-1] + '"'
      else:
          arg = str(arg)
      cmd.write(arg)
      n+=1
    cmd.write(")")
    cmd = cmd.getvalue()
    return self._rengine.eval(cmd)

class ProcessRStderr(threading.Thread):
  def __init__(self, stderr, console_output):
    threading.Thread.__init__(self)
    self._console_output = console_output
    self._stderr = stderr
    self._last_error = None

  def run(self):
    line = StringIO.StringIO()
    while True:
      try:
        c = self._stderr.read(1)
      except ValueError:
        break
      if c == "\r":
        continue
      #print repr(c),
      line.write(c)
      if c == "":
        break
      if c == "\n":
        s = line.getvalue()
        if s!=None and RE_ERROR.match(s):
          debug("ERROR1",repr(s))
          self._last_error = s
          debug("STDERR",repr(s))
          self._console_output(s,1)
          line = StringIO.StringIO()
    debug("CLOSE","child_stderr")

  def resetLastError(self):
    self._last_error = None

  def getLastError(self):
    return self._last_error

class ProcessRStdout(threading.Thread):
  def __init__(self, stdout, console_output):
    threading.Thread.__init__(self)
    self._stdout = stdout
    self._console_output = console_output
    self._last_value = None
    self._expect_value = None
    self._expect_event = threading.Event()
    self._block_semaphore = threading.Semaphore()
    self.remove_values_from_output = False

  def begin(self):
    self._block_semaphore.acquire()

  def end(self):
    self._block_semaphore.release()

  def run(self):
    self.process_stdout()

  def process_stdout(self):
    line = StringIO.StringIO()
    while True:
      try:
        c = self._stdout.read(1)
      except ValueError:
        break
      #print repr(c),
      if c == "\r":
        continue
      self.begin()
      line.write(c)
      if c == "":
        break
      if self._expect_value != None:
        s = line.getvalue()
        n = s.find(self._expect_value)
        if n >= 0:
          l = len(self._expect_value)
          s1 = s[:n]
          s2 = s[n+l:]
          line = StringIO.StringIO(s2)
          line.seek(0,2)
          debug("NOTIFY", repr(self._expect_value))
          self._expect_value = None
          self._expect_event.set()
      if c == "\n":
        s = line.getvalue()
        if s!=None and s.startswith("[1] "):
          self._last_value = s
          if not self.remove_values_from_output:
            debug("STDOUT",repr(s))
            self._console_output(s,0)
        else:
            debug("STDOUT",repr(s))
            self._console_output(s,0)
        line = StringIO.StringIO()
      self.end()
    debug("CLOSE","stdout")
    self._expect_event.set()

  def wait(self):
    debug("WAIT", "")
    self._expect_event.wait()
    debug("WAITOK", "")

  def resetLastValue(self):
    self._last_value = None

  def getLastValue(self):
    if self._last_value == None:
      return None
    return RValue(self._last_value)

  def expect(self, value):
    debug("EXPECT", repr(value))
    self._expect_value = value
    self._expect_event.clear()

class REngine_popen(rlib_base.REngine_base):

  def __init__(self, consoleListener=None):
    rlib_base.REngine_base.__init__(self,consoleListener)

    self.__dict__["_prompt"] = None
    self.__dict__["_child"] = None
    self.__dict__["_processRStdout"] = None
    self.__dict__["_processRStderr"] = None
    self.run()

  def run(self):
    if self._child!=None:
      if self._child.poll()==None:
        raise RuntimeError("R is already running")

    self._prompt="@x#x@>"
    if self.getOperatingSystem() == "win":  
      cmd = (self.getRExecPathname(),
        "--ess", # Fuerza sesion interactiva en Windows.
        "--no-restore",
        "--no-save"
      )
    else:
      cmd = (self.getRExecPathname(),
        "--interactive",
        "--no-readline",
        "--no-restore",
        "--no-save"
      )
    
    # Si no forzamos la sesion interactiva, y R arranca en modo batch,
    # ante cualquier error, R se muere.

    debug("CMD",cmd)
    self._child = subprocess.Popen(cmd,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    self._processRStdout = ProcessRStdout(self._child.stdout, self.console_output)
    self._processRStderr = ProcessRStderr(self._child.stderr, self.console_output)
    self._processRStdout.start()
    self._processRStderr.start()
    #
    # wait initial prompt
    self._processRStdout.expect("> ")
    self._processRStdout.wait()
    #
    # Change prompt
    self.eval('options(prompt=paste("@x#x","@>",sep=""), continue=" ")')
    return True

  def eval(self,expr):
    if self._child==None or self._child.poll()!=None:
      raise RuntimeError("R process is dead")
    expr += "\n"
    #
    # Send comman and wait the echo
    self._processRStdout.begin()
    self._processRStdout.resetLastValue()
    self._processRStderr.resetLastError()
    self._processRStdout.expect(self._prompt)
    self._child.stdin.write(expr)
    self._child.stdin.flush()
    self._processRStdout.end()
    self._processRStdout.wait()
    if self._child.poll()!=None:
      raise RuntimeError("R process is dead")
    value = self._processRStdout.getLastValue()
    debug("EVAL",repr(expr))
    debug("VALUE",str(value))
    if self._processRStderr.getLastError() != None:
      debug("ERROR2",str(value))
      raise ValueError(self._processRStderr.getLastError())
    return value

  def get(self, name):
    theclass = str(self.getclass(name))
    if theclass == "function":
      return RFunction(self, name)
    else:
      return self.eval(name)

  def set(self, name, value):
    if isinstance(value,str) or isinstance(value,unicode) :
      value = '"' + repr(value)[1:-1] + '"'
    else:
      value = str(value)
    self.eval("%s <- %s" % (name,value))

  def getclass(self, name):
    x = self.eval('class(%s)' % name)
    if x == None:
      return None
    return str(x)

  def source(self, pathname):
    return self.eval('source("%s")' % self.getPathName(pathname))

  def end(self):
    self._child.stdin.close()
    self._child.stdout.close()
    self._child.stderr.close()

  def __getattr__(self,name):
    try:
      return self.get(name)
    except ValueError as e:
      raise AttributeError(str(e))

  def __setattr__(self, name, value):
    if name in self.__dict__.keys():
      self.__dict__[name] = value
    else:
      self.set(name, value)

  def isdead(self):
    return self._child.poll()!=None

def getREngine(consoleListener=None):
    return REngine_popen(consoleListener)

