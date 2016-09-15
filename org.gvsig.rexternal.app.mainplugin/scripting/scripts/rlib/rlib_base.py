
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
    return self.getLayerPath(layer)!=None

  def getLayerDir(self, layer):
    """
    Gets the directory in which the layer is stored
    
    :param layer:     A DAL or Sextante layer, or a File object
    :return:          A string representing the path
    """
    pathname = self.getLayerPath(layer)
    return os.path.dirname(pathname)

  def getLayerName(self,layer):
    """
    Gets the layer name as expected by OGR (without extension)
    
    :param layer:     A DAL or Sextante layer, or a File object
    :return:         A string representing the layer name
    """
    pathname = self.getLayerPath(layer)
    return os.path.splitext(os.path.basename(pathname))[0]

  def getTablePath(self,table,unix_sep=False):
    getDbObj = getattr(table,"getBaseDataObject", None)
    if getDbObj != None
      tbl = getDbObj()
      return self.getLayerPath(tbl,unix_sep)

  def getTableName(self,table,unix_sep=False):
    getDbObj = getattr(table,"getBaseDataObject", None)
    if getDbObj != None
      tbl = getDbObj()
      return self.getLayerName(tbl,unix_sep)

  def getLayerPath(self,layer,unix_sep=False):
    """
    Gets the absolute path to the layer file

    :param layer:     A DAL or Sextante layer, or a File object
    :param unix_sep:  Converts the path to unix-style path separator
                     ("/"), regardless the platform in which gvSIG
                     is running. The default is to use the default
                     platform separators
    :return:          A string representing the path
    """
    pathname = layer
    getDataStore = getattr(pathname,"getDataStore", getattr(pathname,"getFeatureStore", None))
    if getDataStore != None:
      store = getDataStore()
      getParameters = getattr(store,"getParameters",None)
      if getParameters == None:
        return None
      parameters = getParameters()
      getFile = getattr(parameters,"getFile",None)
      if getFile == None:
        getURI = getattr(parameters,"getURI",None)
        if getURI == None:
          return None
        pathname = getURI().toString()
      else:
        pathname = getFile()
    if pathname:
      if  getattr(pathname, "getAbsolutePath", None):
        pathname = pathname.getAbsolutePath()
      pathname = os.path.normpath(pathname)
      if unix_sep:
        if isinstance(pathname,str) or isinstance(pathname,unicode):
          pathname = pathname.replace("\\","/")
    return pathname

  def getPathName(self,pathname):
    """
    Deprecated. Use getLayerPath
    """
    return self.getLayerPath(pathname)

  def getLayerDSN(self,pathname):
    """
    Deprecated. Use getLayerDir
    """
    return self.getLayerDir(pathname)

