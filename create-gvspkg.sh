#/bin/bash

if [ ! -d packageinfo ] ; then
  echo "Script must be run from the project base dir"
  exit 1 ;
fi

mkdir -p dist
source packageinfo/package.info.vars
echo "Previous build number": $buildNumber
declare -i newbuildNumber=${buildNumber}+1
buildNumber=${newbuildNumber}
echo "Updated build number: " ${buildNumber}
currdate=`date -R`
sed -e "s/#dateheader#/${currdate}/g" -e "s/#javaversion#/${javaversion}/g" -e "s/#gvSIGversion#/${gvSIGversion}/g"  -e "s/#version#/${version}/g" -e "s/#state#/${state}/g" -e "s/#architecture#/${architecture}/g" -e "s/#operatingsystem#/${operatingsystem}/g" -e "s/#modelversion#/${modelversion}/g" -e "s/#buildNumber#/${buildNumber}/g" -e "/^download-url=.*$/d" packageinfo/package.info.tpl >  org.gvsig.rexternal.app.mainplugin/package.info
zip -9yr dist/gvSIG-desktop-${gvSIGversion}-org.gvsig.rexternal.app.mainplugin-${version}-${buildNumber}-${state}-${operatingsystem}-${architecture}-${javaversion}.gvspkg org.gvsig.rexternal.app.mainplugin

mkdir -p tmp/org.gvsig.rexternal.app.mainplugin
sed -e "s/#dateheader#/${currdate}/g" -e "s/#javaversion#/${javaversion}/g" -e "s/#gvSIGversion#/${gvSIGversion}/g"  -e "s/#version#/${version}/g" -e "s/#state#/${state}/g" -e "s/#architecture#/${architecture}/g" -e "s/#operatingsystem#/${operatingsystem}/g" -e "s/#modelversion#/${modelversion}/g" -e "s/#buildNumber#/${buildNumber}/g" packageinfo/package.info.tpl > tmp/org.gvsig.rexternal.app.mainplugin/package.info
cd tmp
zip -9yr ../dist/gvSIG-desktop-${gvSIGversion}-org.gvsig.rexternal.app.mainplugin-${version}-${buildNumber}-${state}-${operatingsystem}-${architecture}-${javaversion}.gvspki org.gvsig.rexternal.app.mainplugin
cd ..
rm -Rf tmp

sed -e "s/^buildNumber=.*$/buildNumber=${buildNumber}/g" packageinfo/package.info.vars > packageinfo/package.info.vars.new
rm packageinfo/package.info.vars
mv packageinfo/package.info.vars.new packageinfo/package.info.vars
