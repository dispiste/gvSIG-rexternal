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

#uselib.use_plugin("org.gvsig.rexternal.app.mainplugin")

import rlib
reload(rlib)

def console(msg,otype=0):
  print msg,

 
class RProcess(ToolboxProcess):
    def __init__(self, rscript, wd=None):
        self.rscript = rscript
        self.wd = None
 
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
            layer = param.getParameterValueAsVectorLayer()
            return { "dsn": rlib.getLayerPath(layer), "layer": rlib.getLayerName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterRasterLayer").isInstance(parameter):
            layer = param.getParameterValueAsRasterLayer()
            return { "dsn": rlib.getLayerPath(layer), "layer": rlib.getLayerName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterTable").isInstance(parameter):
            return getTablePath
            table = param.getParameterValueAsTable()
            return { "dsn": rlib.getTablePath(layer), "layer": rlib.getTableName(layer)}
        if Class.forName("es.unex.sextante.parameters.ParameterBand").isInstance(parameter):
            return parameter.getParameterValueAsInt()
        if Class.forName("es.unex.sextante.parameters.ParameterString").isInstance(parameter):
            return = parameter.getParameterValueAsString()
        if Class.forName("es.unex.sextante.parameters.ParameterBoolean").isInstance(parameter):
            return parameter.getParameterValueAsBoolean()
        if Class.forName("es.unex.sextante.parameters.ParameterNumericalValue").isInstance(parameter):
            try:
                if parameter.getParameterAdditionalInfo().getType()==AdditionalInfoNumericalValue.NUMERICAL_VALUE_INTEGER:
                    return parameter.getParameterValueAsInt()
            except:
                pass
            return = parameter.getParameterValueAsDouble()


    def _prepare_params(self):
        """Converts the algorithm parameters to a R-friendly array of values"""
        params = self.getParameters()
        i = 0
        while i < params.getNumberOfParameters():
            param = params.getParameter(i)
            name = param.getParameterName()
            value = self._getParamValue(param)
            args[name] = value
            i = i + 1 
        args = {}
        return args

    def processAlgorithm(self):
        """
        Prepares the parameters and calls the R script.
        It can be overriden by subclasses if finer control is required for
        parameter preprocessing
        """
        try:
            #logger = LoggerFactory.getLogger(ToolboxProcess.getClass())
            #logger.error("hello world")
            self.R = rlib.getREngine(console)
            args = self._prepare_params()
            inputLayer = params.getParameter("LAYER")
            if self.wd:
                self.R.setwd(self.wd)
            self.R.source(self.rscript)
            self.callRProcess(args)
            R.end()
        finally:
            print "Process finished %s" % self.getCommandLineName()
            return True
 
    def callRProcess(self, *args):
        """
        Calls the main method of the defined R script
        """
        self.R.call("main", args)

