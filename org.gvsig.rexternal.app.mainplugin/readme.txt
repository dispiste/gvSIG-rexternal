
La version de R esta extraida de OSGEO live 9.0 (Ubuntu 14.04.3 x86).

Los paquetes de R que se incluyen son los instalados con los comandos:

  install.packages(c(
    'stpp','rgdal','maptools','splancs','spatstat','mgcv','BB','bbmle','plyr','raster',
    'sqldf','lubridate','rgeos','RPostgreSQL','RODBC','pixmap','sp','spdep','RColorBrewer',
    'foreign','plotrix','geoR','fields','maps', 'gridExtra','tweet2r','ggmap','ROAuth','RSQLite',
    'ggplot2','streamR', 'scales'
  ))
  install.packages('INLA', repos='http://www.math.ntnu.no/inla/R/stable')

Una vez instalados en el LiveDVD se copiara la carpeta

  /usr/local/lib/R/site-library

del LiveDVD sobre la carpeta:

  gvSIG/extensiones/org.gvsig.r.app.mainplugin/R/site-library

De la instalacion de gvSIG.

