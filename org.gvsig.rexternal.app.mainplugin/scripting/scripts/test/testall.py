# encoding: utf-8

import rlib
reload(rlib)
from rlib.process import *
import os

"""
Sample plugin for declaring R plugins using RExternal plugin

Note that it is CRUCIAL that each process (each class extending from 
RProcess) has a unique name (even across different plugins!!!!). Otherwise
Sextante history gets confused and some errors arise.

Author: Cesar Martinez Izquierdo
"""

class TestProcessAll(RProcess):
    """
    We omit __init__ in this class (we use self.rscript and self.wd in defineCharacteristics instead)
    We also omit callRProcess (as we have a main method in the test2.r script)
    """
    def defineCharacteristics(self):
        plugin = PluginsLocator.getManager().getPlugin("org.gvsig.rexternal.app.mainplugin")
        pluginFolder = plugin.getPluginDirectory().getAbsoluteFile()
        self.rscript = os.path.join(str(pluginFolder), "scripting/scripts/test/data", "test2.r")
        self.wd = os.path.join(str(pluginFolder), "scripting/scripts/test/data")
        # Process name
        self.setName("Test R process all")
        # Process group
        self.setGroup("R processes")
        params = self.getParameters()
        # Define an input vector parameter, named IN_VECTOR, of type polygon and make it mandatory
        params.addInputVectorLayer("IN_VECTOR","Input vector layer", SHAPE_TYPE_POLYGON, True)

        # Define an input raster parameter named IN_RASTER and make it mandatory
        params.addInputRasterLayer("IN_RASTER","Input raster layer", True)

        # Define an input raster parameter named IN_RASTER and make it mandatory
        params.addInputTable("IN_TABLE","Input table layer", True)

        params.addString("IN_STR","Input string")
        params.addBoolean("IN_BOOL","Input bool", True)
        params.addNumericalValue("IN_INT","Input int", 0, NUMERICAL_VALUE_INTEGER)
        params.addNumericalValue("IN_DOUBLE","Input float", 0.0, NUMERICAL_VALUE_DOUBLE)

        # Define an output raster layer, name "OUT_RASTER"
        #self.addOutputRasterLayer("OUT_RASTER", "Output raster")

    def callRProcess(self, *args):
        print args


def main(*args):
    process = TestProcessAll()
    process.selfregister("Scripting")
    process.updateToolbox()

