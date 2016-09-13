
from gvsig import *

from org.apache.commons.io import FilenameUtils
from org.gvsig.andami import Utilities
import os

class REngine_base(object):
  def __init__(self, consoleListener=None):
    self.__dict__["_consoleListeners"] = None
    self.__dict__["_architecture"] = None
    self.__dict__["_operatingSystem"] = None
    
    self._consoleListeners = list()
    self.addConsoleListener(consoleListener)

  def source(self,pathname):
    return None

  def eval(self,expresion):
    return None

  def end(self):
    self._consoleListeners = list()

  def abort(self):
    pass
    
  def get(self, name):
    pass

  def set(self,name,value):
    pass

  def call(self, funcname, *args):
    pass
    
  def run(self):
    return True

  def getTemp(self,basename=None):
    if basename == None:
      return Utilities.TEMPDIRECTORYPATH
    return os.path.normpath(Utilities.TEMPDIRECTORYPATH + "/" + basename)
    
  def addConsoleListener(self, function):
    if function == None:
      return
    self._consoleListeners.append(function)

  def console_output(self, text, otype=0):
    for listener in self._consoleListeners:
      try:
        listener(text,otype)
      except Exception as ex:
        print "Error calling console listener %s. %s" % (repr(listener), str(ex))

  def getArchitecture(self):
    if self._architecture == None:
      from org.gvsig.tools import ToolsLocator

      pkgmanager = ToolsLocator.getPackageManager()
      self._operatingSystem = pkgmanager.getOperatingSystemFamily()
      self._architecture = pkgmanager.getArchitecture()
    return self._architecture
    
  def getOperatingSystem(self):
    if self._operatingSystem == None:
      from org.gvsig.tools import ToolsLocator

      pkgmanager = ToolsLocator.getPackageManager()
      self._operatingSystem = pkgmanager.getOperatingSystemFamily()
      self._architecture = pkgmanager.getArchitecture()
    return self._operatingSystem
    
  def getRExecPathname(self):
    from java.io import File
    from org.gvsig.andami import PluginsLocator

    plugin = PluginsLocator.getManager().getPlugin("org.gvsig.rexternal.app.mainplugin")
    pluginFolder = plugin.getPluginDirectory().getAbsoluteFile()

    # create and load default properties
    from java.util import Properties
    from java.io import FileInputStream
    conf = Properties()
    in_stream = FileInputStream(File(pluginFolder, "rpath.properties"))
    conf.load(in_stream)
    in_stream.close()
    Rexe = conf.getProperty("R_BIN_PATH")
    if Rexe!="":
      if os.path.exists(Rexe):
        return Rexe
      elif not os.path.isabs(Rexe):
        if os.path.exists(os.path.join(pluginFolder.toString(), Rexe)):
          return os.path.join(pluginFolder.toString(), Rexe)

    ## if R_BIN_PATH is empty, search Rexe in system path
    if self.getOperatingSystem() == "win":
      Rcmd = "R.exe"
    else:
      Rcmd = "R"
    for d in os.environ['PATH'].split(os.path.pathsep):
      Rexe = os.path.join(d, Rcmd)
      if os.path.exists(Rexe):
        return Rexe
    raise Exception("Operating system not supported.")


  def isLayerSupported(self,layer):
    return self.getPathName(layer)!=None

  def getLayerDSN(self,pathname):
    pathname = self.getPathName(pathname)
    return os.path.normpath(FilenameUtils.getFullPath(pathname))

  def getLayerName(self,pathname):
    pathname = self.getPathName(pathname)
    return FilenameUtils.getBaseName(pathname)

  def getPathName(self,pathname):
    getDataStore = getattr(pathname,"getDataStore", None)
    if getDataStore == None:
      getAbsolutePath = getattr(pathname,"getAbsolutePath",None)
      if getAbsolutePath!=None:
        pathname = getAbsolutePath()
    else:
      store = getDataStore()
      getParameters = getattr(store,"getParameters",None)
      if getParameters == None:
        return None
      parameters = getParameters()
      getFile = getattr(parameters,"getFile",None)
      if getFile == None:
        return None
      pathname = getFile()
      if pathname == None:
        return None
      pathname = pathname.getAbsolutePath()

    if isinstance(pathname,str) or isinstance(pathname,unicode):
      return pathname.replace("\\","/")
    return None



