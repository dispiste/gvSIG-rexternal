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

    def getParamValue(self, parameter, asPlainType=False):
        """
        Gets the value of the parameter

        :param parameter:   The parameter name or parameter instance object
        :param asPlainTye:  If True, the value is converted to a plain Python type
                            (numeric, string, boolean or tuple) which can be easily
                            fed to R
        """
        if isinstance(parameter, basestring):
          params = self.getParameters()
          parameter = params.getParameter(parameter)
        if Class.forName("es.unex.sextante.parameters.ParameterVectorLayer").isInstance(parameter):
            layer = parameter.getParameterValueAsVectorLayer()
            if asPlainType:
              return (self.R.getLayerPath(layer), self.R.getLayerName(layer))
            else:
              return layer
        if Class.forName("es.unex.sextante.parameters.ParameterRasterLayer").isInstance(parameter):
            layer = parameter.getParameterValueAsRasterLayer()
            if asPlainType:
              return self.R.getLayerPath(layer)
            else:
              return layer
        if Class.forName("es.unex.sextante.parameters.ParameterTable").isInstance(parameter):
            table = parameter.getParameterValueAsTable()
            if asPlainType:
              return self.R.getLayerPath(table)
            else:
              return table
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
        args = ()
        params = self.getParameters()
        i = 0
        while i < params.getNumberOfParameters():
            param = params.getParameter(i)
            value = self.getParamValue(param, True)
            args += value
            i = i + 1
        return args
        
    def _prepare_outputs(self):
        outputs = ()
        outputSet = self.getOutputObjects()
        i = 0
        while i < outputSet.getOutputObjectsCount():
          output = outputSet.getOutput(i)
          outputName = output.getName()
          if Class.forName("es.unex.sextante.outputs.OutputVectorLayer").isInstance(output):
            outLayerPath = self.getOutputChannel(outputName).toString()
            outLayerName = self.R.getLayerName(outLayerPath)
            outputs += (outLayerPath, outLayerName)
          elif Class.forName("es.unex.sextante.outputs.OutputRasterLayer").isInstance(output):
            outLayerPath = self.getOutputChannel(outputName).toString()
            outputs += (outLayerPath,)
          elif Class.forName("es.unex.sextante.outputs.OutputTable").isInstance(output):
            outLayerPath = self.getOutputChannel(outputName).toString()
            outputs += (outLayerPath,)
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
            params = self._prepare_params()
            outputs = self._prepare_outputs()
            args = params + outputs
            if self.wd:
                self.R.setwd(self.wd)
            self.R.source(self.rscript)
            self.callRProcess(*args)
            self.R.end()
            
        finally:
            print "Process finished %s" % self.getCommandLineName()
            return True
 
    def callRProcess(self, *args):
        """
        Calls the main method of the defined R script
        """
        self.R.call("main", *args)


