
#
# Funcion encargada de cargar las librerias necesarias
#
load_libraries <- function() {
  library(rgdal)
  library(raster)
  return(1)
}

#
# Funcion a ejecutar
# El nombre de la funcion variara segun el modelo
# que se este ejecutando.
#
# - los archivos asociados a capas vectoriales (shapes), 
#   se pasan con dos parametos, path y nombre (sin extension).
# - Los raster con la ruta completa.
#
doalmostnothing<-function(shpdsn, shpname,rasterpathname){
  shp<-readOGR(dsn=shpdsn,layer=shpname)
  message("shp loaded")
  rasterimage<-raster("sombrejat.tif")
  message("raster loaded")
  writeRaster(rasterimage, filename=rasterpathname, format="GTiff", overwrite=TRUE)
  return (1)
}



