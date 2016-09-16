# encoding: utf-8

from gvsig import *
from gvsig.commonsdialog import *

from gvsig.libs.toolbox import *
from es.unex.sextante.dataObjects import IRasterLayer, IVectorLayer
from  es.unex.sextante.additionalInfo import AdditionalInfoNumericalValue
from org.gvsig.geoprocess.lib.api import GeoProcessLocator
from java.lang import Class

from gvsig import uselib
from org.gvsig.andami import PluginsLocator
import os
from org.apache.commons.io import FilenameUtils
from org.slf4j import LoggerFactory

#uselib.use_plugin("org.gvsig.rexternal.app.mainplugin")

import rlib_simplepopen
import rlib_base
#reload(rlib)

def console(msg,otype=0):
  logger(msg)
  #print msg,

 
class RProcess(ToolboxProcess):
    def __init__(self, rscript, wd=None):
        self.rscript = rscript
        self.wd = wd
        ToolboxProcess.__init__(self)
 
    def defineCharacteristics(self):
        """
        Define the input and output parameters from our process.
        To be implemented by subclasses.

        # Example:
        # Process name
        self.setName("Test rgdal")
        # Process group
        self.setGroup("R processes")
        params = self.getParameters() 
        # Define an input parameter, named LAYER, of type polygon and make it mandatory
        params.addInputVectorLayer("LAYER","Capa de entrada", SHAPE_TYPE_POLYGON, True)
        # Define an output raster layer, name "RESULT_LAYER"
        self.addOutputRasterLayer("RESULT_RASTER", "Output raster")
        """
        pass

    def _getParamValue(self, parameter):
        if Class.forName("es.unex.sextante.parameters.ParameterVectorLayer").isInstance(parameter):
            layer = parameter.getParameterValueAsVectorLayer()
            self.R.getLayerPath(layer)
            self.R.getLayerName(layer)
            return { "dsn": self.R.getLayerPath(layer), "layer": self.R.getLayerName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterRasterLayer").isInstance(parameter):
            layer = parameter.getParameterValueAsRasterLayer()
            dsn = self.R.getLayerPath(layer)
            return { "dsn": dsn, "layer": self.R.getLayerName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterTable").isInstance(parameter):
            return getTablePath
            table = parameter.getParameterValueAsTable()
            return { "dsn": self.R.getTablePath(layer), "layer": self.R.getTableName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterBand").isInstance(parameter):
            return parameter.getParameterValueAsInt()
        if Class.forName("es.unex.sextante.parameters.ParameterString").isInstance(parameter):
            return parameter.getParameterValueAsString()
        if Class.forName("es.unex.sextante.parameters.ParameterBoolean").isInstance(parameter):
            return parameter.getParameterValueAsBoolean()
        if Class.forName("es.unex.sextante.parameters.ParameterNumericalValue").isInstance(parameter):
            try:
                if parameter.getParameterAdditionalInfo().getType()==AdditionalInfoNumericalValue.NUMERICAL_VALUE_INTEGER:
                    return parameter.getParameterValueAsInt()
            except:
                pass
            return parameter.getParameterValueAsDouble()

    def _prepare_params(self):
        """Converts the algorithm parameters to a R-friendly array of values"""
        args = {}
        params = self.getParameters()
        i = 0
        while i < params.getNumberOfParameters():
            param = params.getParameter(i)
            self.tmplogger.write(str(param)+"\n")
            name = param.getParameterName()
            self.tmplogger.write("prep2\n")
            value = self._getParamValue(param)
            self.tmplogger.write("prep3\n")
            args[name] = value
            i = i + 1
        self.tmplogger.write("prep4\n")
        return args
        
    def _prepare_outputs(self):
        outputs = {}
        outputSet = self.getOutputObjects()
        i = 0
        while i < outputSet.getOutputObjectsCount():
          output = outputSet.getOutput(i)
          outputName = output.getName()
          outLayerPath = self.getOutputChannel(outputName).toString()
          outLayerName = self.R.getLayerName(outLayerPath)
          outputs[outputName] = { "dsn": outLayerPath, "layer": outLayerName}
          i = i + 1
        
        return outputs

    def processAlgorithm(self):
        """
        Prepares the parameters and calls the R script.
        It can be overriden by subclasses if finer control is required for
        parameter preprocessing
        """
        try:            
            self.R = rlib_simplepopen.getREngine(console)
            args = self._prepare_params()
            outputs = self._prepare_outputs()
            args.update(outputs)
            if self.wd:
                self.R.setwd(self.wd)
            self.R.source(self.rscript)
            self.callRProcess(**args)
            self.R.end()
            
        finally:
            print "Process finished %s" % self.getCommandLineName()
            return True
 
    def callRProcess(self, *args):
        """
        Calls the main method of the defined R script
        """
        self.R.call("main", args)


