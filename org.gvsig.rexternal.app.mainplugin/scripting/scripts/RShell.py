
from gvsig import *
from gvsig.commonsdialog import *
from rlib import rlib_base
import os

def isexe(fpath):
  return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        
def RShellWindows():
  RExe = rlib_base.REngine_base().getRExecPathname()
  cmd='start "R terminal" /wait "%s" --ess --no-restore --no-save' % RExe
  os.system(cmd)

def RShellLinux():
  RExe = rlib_base.REngine_base().getRExecPathname()
  if isexe("/usr/bin/x-terminal-emulator"):
    cmd = '/usr/bin/x-terminal-emulator -e "%s" --interactive --no-restore --no-save &' % RExe
  elif isexe("/usr/bin/konsole"):
    cmd = '/usr/bin/konsole -e "%s" --interactive --no-restore --no-save &' % RExe
  else:
    cmd='xterm -sb -rightbar -sl 1000 -fg gray -bg black -e "%s" --interactive --no-restore --no-save &' % RExe
  os.system(cmd)

def RShellMac():
  RExe = rlib_base.REngine_base().getRExecPathname()
  # FIXME: never tested
  cmd = 'open -a Terminal.app -e "%s" --interactive --no-restore --no-save &' % RExe
  os.system(cmd) 

def main(*args):
  from org.gvsig.tools import ToolsLocator
  pkgmanager = ToolsLocator.getPackageManager()
  operatingSystem = pkgmanager.getOperatingSystemFamily()
  #architecture = pkgmanager.getArchitecture()

  if operatingSystem == "win":
    RShellWindows()
  
  elif operatingSystem == "lin":
    RShellLinux()
  elif "mac" in operatingSystem or "darwin" in operatingSystem:
    RShellMac()

  else:
    msgbox("Can't launch R console, don't identify the OS (%s)." % operatingSystem)

    
