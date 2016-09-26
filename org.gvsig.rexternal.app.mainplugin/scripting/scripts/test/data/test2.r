# encoding: utf-8

load_libraries <- function() {
  library(rgdal)
  library(raster)
  return(1)
}

doalmostnothing <- function(shpdsn, shpname, inrasterpathname, outrasterpathname){
  shp<-readOGR(dsn=shpdsn,layer=shpname)
  message("shp loaded")
  rasterimage<-raster(inrasterpathname)
  message("raster loaded")
  writeRaster(rasterimage, filename=outrasterpathname, format="GTiff", overwrite=TRUE)
  return (1)
}

main <- function(shpdsn, shpname, inrasterpathname, outrasterpathname){
    load_libraries()
    doalmostnothing(shpdsn, shpname, inrasterpathname, outrasterpathname)
    return (1)
}
