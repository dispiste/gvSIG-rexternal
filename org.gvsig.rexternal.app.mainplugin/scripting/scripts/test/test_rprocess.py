# encoding: utf-8

import gvsig
import rlib
reload(rlib)
from rlib.process import RProcess
from org.gvsig.andami import PluginsLocator
import os
from es.unex.sextante.dataObjects import IRasterLayer, IVectorLayer
from gvsig import commonsdialog

class TestProcess(RProcess):
    def __init__(self):
        plugin = PluginsLocator.getManager().getPlugin("org.gvsig.rexternal.app.mainplugin")
        pluginFolder = plugin.getPluginDirectory().getAbsoluteFile()
        rscript = os.path.join(str(pluginFolder), "scripting/scripts/test/data", "test.r")
        wd = os.path.join(str(pluginFolder), "scripting/scripts/test/data")
        RProcess.__init__(self, rscript, wd)

    def defineCharacteristics(self):
        # Process name
        self.setName("Test rprocess")
        # Process group
        self.setGroup("R processes")
        params = self.getParameters() 
        # Define an input parameter, named LAYER, of type polygon and make it mandatory
        params.addInputVectorLayer("LAYER","Input layer", IVectorLayer.SHAPE_TYPE_POLYGON, True)
        # Define an output raster layer, name "RESULT_RASTER"
        self.addOutputRasterLayer("RESULT_RASTER", "Output raster")
        
    def callRProcess(self, *args):
        """
        Calls the main method of the defined R script
        """
        self.R.call("load_libraries")
        self.R.call("doalmostnothing", *args)
        """
        Alternative way to individually access each parameter
        layerDsn = args[0]
        layerName = args[1]
        outDsn = args[2]
        self.R.call("doalmostnothing", layerDsn, layerName, outDsn)
        """
        
        """
        Alternative way2 to directly access params by name
        # this gets a gvSIG/Sextante layer:
        in_layer = self.getParamValue("LAYER")
        # we use rlib to convert the layer to an OGR DSN and an OGR layer name
        layerDsn = rlib.getLayerPath(in_layer)
        layerName = rlib.getLayerName(in_layer)
        # for output layers, getOutputValue directly returns a path, as the layer does not exist yet
        outDsn = self.getOutputValue("RESULT_RASTER")
        self.R.call("doalmostnothing", layerDsn, layerName, outDsn)
        """

def main(*args):
        process = TestProcess()
        process.selfregister("Scripting")
        process.updateToolbox()

