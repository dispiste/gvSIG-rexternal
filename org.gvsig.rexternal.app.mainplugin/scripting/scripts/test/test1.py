
from gvsig import *
import os

import rlib
reload(rlib)

def console(msg,otype=0):
  print msg,

def main(*args):
  R = rlib.getREngine(console)
  layer = os.path.join(str(script.getResource("data")), "contorno.shp")
  R.setwd(R.getLayerPath(script.getResource("data")))
  R.source( R.getLayerPath(script.getResource("data/test.r")) )
  R.call("load_libraries")
  R.call("doalmostnothing", 
    R.getLayerPath(layer),
    R.getLayerName(layer),
    R.getTemp("r-output.tif")
  )
  R.end()

  """
<rprocess>
  <name>Proceso R de prueba</name>
  <group>Vectorial</group>
  <inputs>
    <input>
      <type>VectorLayer</type>
      <name>LAYER</name>
      <label>Capa vetorial de prueba</label>
      <shapetype>LINE</shapetype>
    </input>
    <input>
      <type>NumericalValue</type>
      <name>X</name>
      <label>Valor de X inicial</label>
      <valuetype>DOUBLE</valuetype>
    </input>
  </inputs>
  <outputs>
    <output>
      <type>VectorLayer</type>
      <name>X</name>
      <label>no se que poner aqui</label>
      <shapetype>LINE</shapetype>
    </output>
  </outputs>
</rprocess>

  """

