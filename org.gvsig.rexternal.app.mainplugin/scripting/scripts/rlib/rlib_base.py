
from gvsig import *

from org.apache.commons.io import FilenameUtils
from org.gvsig.andami import Utilities
from org.gvsig.tools import ToolsLocator
from org.gvsig.andami import PluginsLocator
from java.io import File
import os
from java.util import Properties
from java.io import FileInputStream

# it seems that the execution context is the one of the scripting plugin,
# so we need to explicitly declare the dependence to rexternal plugin to access
# jna-platform jars
from gvsig import uselib
uselib.use_plugin("org.gvsig.rexternal.app.mainplugin")


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
      pkgmanager = ToolsLocator.getPackageManager()
      self._operatingSystem = pkgmanager.getOperatingSystemFamily()
      self._architecture = pkgmanager.getArchitecture()
    return self._architecture
    
  def getOperatingSystem(self):
    if self._operatingSystem == None:
      pkgmanager = ToolsLocator.getPackageManager()
      self._operatingSystem = pkgmanager.getOperatingSystemFamily()
      self._architecture = pkgmanager.getArchitecture()
    return self._operatingSystem
    
  def getRExecPathname(self):
    plugin = PluginsLocator.getManager().getPlugin("org.gvsig.rexternal.app.mainplugin")
    pluginFolder = plugin.getPluginDirectory().getAbsoluteFile()

    # create and load default properties
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

    ## if R_BIN_PATH is empty, search for Rexe
    path = self._getFromRegistry()
    if path:
      return path
    path = self._getFromWellKnownDirs()
    if path:
      return path
    # search in system PATH as last resort
    path = self._searchInPath()
    if path:
      return path
    raise Exception("Automatic detection failed. Set R_BIN_PATH in rpath.properties")

  def _getFromRegistry(self):
    if self.getOperatingSystem() == "win":
      try:
        rbasepath = None
        from com.sun.jna.platform.win32 import Advapi32Util
        from com.sun.jna.platform.win32 import WinReg
        versionKeyPath = "Software\R-core\R"
        versionKey = "Current Version"
        rKeyPath = "Software\R-core\R\%s"
        rKey = "InstallPath"
        version = Advapi32Util.registryGetStringValue(WinReg.HKEY_LOCAL_MACHINE, versionKeyPath, versionKey)
        if version:
          rbasepath = Advapi32Util.registryGetStringValue(WinReg.HKEY_LOCAL_MACHINE, rKeyPath%(version), rKey)
        else:
          version = Advapi32Util.registryGetStringValue(WinReg.HKEY_CURRENT_USER, versionKeyPath, versionKey)
          if version:
            rbasepath = Advapi32Util.registryGetStringValue(WinReg.HKEY_CURRENT_USER, rKeyPath%(version), rKey)
        if rbasepath:
          if "64" in self.getArchitecture():
            suffix = "bin/x64/R.exe"
          else:
            suffix = "bin/i386/R.exe"
          if os.path.exists(os.path.join(rbasepath, suffix)):
            return os.path.join(rbasepath, suffix)
      except:
        pass
            
  def _getFromWellKnownDirs(self):
    if self.getOperatingSystem() == "win":
      # search for paths like: C:/Program Files/R/R-3.2.3/bin/x64/R.exe
      programFiles = "C:/Program Files"
      try:
        # try to get the localized version of Program Files
        from com.sun.jna.platform.win32 import Shell32Util
        from com.sun.jna.platform.win32 import ShlObj
        path = Shell32Util.getFolderPath(ShlObj.CSIDL_PROGRAM_FILES)
        if path:
            programFiles = path
      except:
          pass
      basedir = os.path.join(programFiles, "R")
      # We'll search for both 64 and 32 bits of R, as they should
      # work correctly regardless the architecture of the JVM.
      # But try the architecture of the JVM first
      if "64" in self.getArchitecture():
        suffixes = ["bin/x64/R.exe", "bin/i386/R.exe"]
      else:
        suffixes = ["bin/i386/R.exe", "bin/x64/R.exe"]
      for suffix in suffixes:
        for d in os.listdir(basedir):
          if os.path.exists(os.path.join(basedir, d, suffix)):
            return os.path.join(basedir, d, suffix)
    else:
      # Linux and Mac 
      if os.path.exists("/usr/bin/R"):
        return "/usr/bin/R"
      elif os.path.exists("/usr/local/bin/R"):
        return "/usr/local/bin/R"
      elif os.path.exists("/opt/local/bin/R"):
        return "/opt/local/bin/R"
      elif os.path.exists("/Library/Frameworks/R.framework/Current/Resources/bin/R"):
        return "/Library/Frameworks/R.framework/Current/Resources/bin/R"

  def _searchInPath(self):
    if self.getOperatingSystem() == "win":
      cmd = "R.exe"
    else:
      cmd = "R"
    for d in os.environ['PATH'].split(os.path.pathsep):
      Rexe = os.path.join(d, Rcmd)
      if os.path.exists(Rexe):
        return Rexe        

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

  def normalizePath(self, path, unix_sep=True):
    """
    Converts to absolute path, normalizes (making all the path separators homogeneous)
    and optionally converts to unix separator style
    """
    if path:
      if getattr(path, "getAbsolutePath", None):
        path = path.getAbsolutePath()
      path = os.path.normpath(path)
      if unix_sep:
        if isinstance(path,str) or isinstance(path,unicode):
          path = path.replace("\\","/")
    return path

  def getTablePath(self,table,unix_sep=True):
    getDbObj = getattr(table,"getBaseDataObject", None)
    if getDbObj != None:
      table = getDbObj()
    if getattr(table, "getStore", None):
      store = table.getStore()
      if getattr(store, "getParameters", None):
        params = store.getParameters()
        dbfFile = getattr(params, "dbfFile", None)
        if dbfFile:
          dbfFile = self.normalizePath(dbfFile, unix_sep)
          return dbfFile
        else:
          getDbf = getattr(params, "getDBFFile", None)
          if getDbf:
            dbfFile = getDbf()
            dbfFile = self.normalizePath(dbfFile, unix_sep)
            return dbfFile
    return self.getLayerPath(table,unix_sep)

  def getTableName(self,table):
    p = self.getTablePath(table)
    return os.path.splitext(os.path.basename(pathname))[0]

  def getLayerPath(self,layer,unix_sep=True):
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
    getBaseDataObject = getattr(pathname,"getBaseDataObject", None)
    if getBaseDataObject:
        pathname = getBaseDataObject()
    getDataStore = getattr(pathname,"getDataStore", getattr(pathname,"getFeatureStore", getattr(pathname,"getStore", None)))
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
	return self.normalizePath(pathname, unix_sep)

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


