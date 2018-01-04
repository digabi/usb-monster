#!/bin/bash

set -e

mkdir -p deb-root/usr/local/lib/digabi-dd-curses

cp $(git ls-files | grep -v create-deb.sh) deb-root/usr/local/lib/digabi-dd-curses/

fpm -C deb-root/ -s dir --name digabi-dd-curses --architecture native -t deb --version "1.0.${BUILD_NUMBER}" --depends pv --depends python .
