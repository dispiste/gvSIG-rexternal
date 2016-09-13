
from gvsig import *

from org.rosuda.JRI import Rengine
from org.rosuda.JRI import RMainLoopCallbacks
from java.io import File
import os
import os.path
import array.array
import jarray
from java.lang import String
import commonsdialog

from rlib_base import REngine_base

class _ProxyFunction(object):
  def __init__(self, R, name):
    self._R = R
    self._name = name

  def __call__(self,*args):
    x = self._R.eval(self._name+"()")
    if x == None:
      return None
    c = x.getContent()
    if isinstance(c,array.array) and len(c)==1:
      return c[0]
    return c
    
class REngine_jri(REngine_base,RMainLoopCallbacks):
  def __init__(self, consoleListener=None):
    REngine_base.__init__(self,consoleListener)
    
    self._R = Rengine.getMainEngine()
    if self._R == None :
      self._R = Rengine(jarray.array([None]*10,String), False, self)
    
  def source(self,pathname):
    if isinstance(pathname,File):
        pathname = pathname.getAbsolutePath()
    pathname = pathname.replace("\\","/")
    x = self._R.eval('source("%s")' % pathname)
    return x
    
  def eval(self,expresion):
    return self._R.eval(expresion)

  def end(self):
    self._R.end()
    REngine_base.end(self)

  def __setattr__(self,name,value):
    if name in ("_R","_consoleListeners"): 
      self.__dict__[name] = value
    else:
      self._R.assign(name,value)

  def __getattr__(self,name):
    x = self._R.eval(name)
    if x == None or x.getContent() == None:
      return _ProxyFunction(self._R,name)
    c = x.getContent()
    if isinstance(c,array.array) and len(c)==1:
      return c[0]
    return c      

  def rBusy(self, re, which):
    #print "rBusy ", witch
    pass
  
  def rChooseFile(self,re, newFile):
    #print "rChooseFile ", newFile
    pass
  
  def rFlushConsole(self,re):
    #print "rFlushConsole "
    pass
  
  def rLoadHistory(self, re, filename):
    #print "rLoadHistory ", filename
    pass

  def rReadConsole(self, re, prompt, addToHistory):
    return inputbox("",prompt)

  def rSaveHistory(self, re, filename):
    #print "rSaveHistory ", filename
    pass

  def rShowMessage(self, re, message):
    commonsdialog.msgbox(message)

  def rWriteConsole(self, re, text, otype):
    #print "[%s] %s" % (otype, text),
    self.console_output(text,otype)
  
def getREngine(consoleListener=None):
    return REngine_jri(consoleListener)


    

