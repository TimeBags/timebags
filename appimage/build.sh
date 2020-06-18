#!/bin/bash

# https://github.com/Appimage/AppImageKit/releases/latest
appimagetool="appimagetool-${HOSTTYPE}.AppImage"
if [ ! -f "$appimagetool" ] ; then
    echo "ERROR: file $appimagetool not found!"
    exit 1
fi
chmod +x $appimagetool

# save workdir path
workdir=$(pwd)

# create appdir
appname="TimeBags-${HOSTTYPE}"
appdir="${workdir}/${appname}.AppDir"
[ -d ${appdir} ] && rm -fr ${appdir}
mkdir ${appdir} || exit 1

# copy template files
cd ${workdir}/Templates/ || exit 1
cp AppRun TimeBags TimeBags.desktop TimeBags.png ${appdir}
echo -e "\e[32mCreated AppDir ${appdir}\e[39m"

# copy app
cp -r ../../target/TimeBags ${appdir}/runtime || exit 1
echo -e "\e[32mApp copied in the AppDir\e[39m"

# build appimage
cd ${workdir} || exit 1
output="${appname}.AppImage"
[ -f ${output} ] && rm -f ${output}
./${appimagetool} -n ${appdir} ${output} || exit 1
echo -e "\e[32mCreated appimage file ${output}\e[39m"

# cleaning
cd ${workdir} || exit 1
rm -fr ${appdir} || exit 1
echo -e "\e[32mAppDir removed.\e[39m"
echo -e "\e[32mSuccess!\e[39m"
