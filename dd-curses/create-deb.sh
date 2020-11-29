#!/bin/bash

set -e

mkdir -p deb-root/usr/local/lib/digabi-dd-curses
cp dd_writer.py digabi-dd-curses digabi-usb-monster.png error.wav ok.wav README.md write_dd.py deb-root/usr/local/lib/digabi-dd-curses/

mkdir -p deb-root/usr/local/bin
cp digabi-usb-monster deb-root/usr/local/bin/

mkdir -p deb-root/usr/share/applications
cp digabi-usb-monster.desktop deb-root/usr/share/applications/

VERSION=`cat VERSION`
if [ -n "${BUILD_NUMBER}" ]; then
  VERSION=${VERSION}.${BUILD_NUMBER}
fi

fpm -C deb-root/ -s dir --name digabi-dd-curses --architecture all -t deb --version ${VERSION} \
  --description "USB monster is a zenity wrapper for dd-curses. This is the Python/Curses\nscript used by Matriculation Examination board to write massive amount of\nUSB sticks in short timeframe." \
  --maintainer "abitti@ylioppilastutkinto.fi" \
  --vendor "Matriculation Examination Board" \
  --depends pv \
  --depends python \
  --depends python-psutil \
  --depends "terminator | xfce4-terminal" \
  --depends zenity \
  --depends unzip \
  .
