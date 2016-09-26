# gvSIG-rexternal
gvSIG plugin which allows to integrate R scripts in the
gvSIG geoprocessing toolbox and to launch R commands from gvSIG Python scripts.

This plugin executes the R code using an external R process and it needs R to be
installed on the system in order to work.

[gvSIG](http://www.gvsig.com) is a free geographic information system (GIS) application. [R](https://www.r-project.org/) is a free software environment for statistical computing and graphics.

## Installation
* gvSIG: version 2.3.0 rc4 or later is required, available on the [development
versions section](http://www.gvsig.com/en/products/gvsig-desktop/development-versions-downloads).
It will be available on the [regular downloads section](http://www.gvsig.com/en/products/gvsig-desktop/downloads)
once gvSIG 2.3.0 is released.
* [R software](https://www.r-project.org/)
* RExternal plugin (.gvspkg): download the last available version from the [dist](https://github.com/dispiste/gvSIG-rexternal/tree/master/dist) folder on this repository

Install gvSIG and R. Then, from the gvSIG Add-on manager, select "Installation
from file" and then select the downloaded .gvspkg file and select RExternal plugin
from the list of available plugins.

Note that you may need to execute gvSIG as Administrator in order to install plugins in Windows

## Configuration
The R executable is usually autodetected by RExternal on Linux, Windows and Mac.

If autodetection fails or you want to use a different R version available on
your system, set the R_BIN_PATH variable on the file gvSIG/extensiones/org.gvsig.rexternal.app.mainplugin/rpath.properties
(within your gvSIG installation).

## Integrating an R script on the gvSIG Toolbox
Have a look at these [example scripts](https://github.com/dispiste/geostat2016/raw/master/scripts/scripts.zip)
and [training materials](https://dispiste.github.io/geostat2016/gvsig-workshop/).

## Calling R commands from gvSIG Python scripts
Have a look to [this example script](https://github.com/dispiste/gvSIG-rexternal/blob/master/org.gvsig.rexternal.app.mainplugin/scripting/scripts/test/test1.py).

## Other R integrations for gvSIG
There is another R integration for gvSIG, based on Renjin (a Java-based R
implementation). The Renjin integration is available in gvSIG without any
additional plugin and provides a totally different set of features (and also
limitations).

The Renjin integration is suitable to script gvSIG (load layers, create
new Views, launch gvSIG Geoprocesses, etc) using R language or to create new
gvSIG processes implemented in R. On the other hand,
only a subset of the existing R packages are available for Renjin.
