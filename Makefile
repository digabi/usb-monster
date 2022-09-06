ifeq ("${GITHUB_RUN_NUMBER}", "")
VERSION_FULL:=$(shell cat src/VERSION)+manual
else
VERSION_FULL:=$(shell cat src/VERSION)+${GITHUB_RUN_NUMBER}
endif

clean:
	- rm -fR temp/
	- rm *.deb

deb: src/* clean
	# USB-monster app
	mkdir -p temp/deb-root/usr/local/lib/digabi-usb-monster
	cp src/dd_writer.py src/digabi-usb-monster.png src/error.wav src/ok.wav src/README.md src/write_dd.py temp/deb-root/usr/local/lib/digabi-usb-monster/

	mkdir -p temp/deb-root/usr/local/bin
	cp src/digabi-usb-monster temp/deb-root/usr/local/bin/

	mkdir -p temp/deb-root/usr/share/applications
	cp src/digabi-usb-monster.desktop temp/deb-root/usr/share/applications/

	mkdir -p temp/deb-root/usr/share/polkit-1/actions
	cp src/polkit/digabi-usb-monster.policy temp/deb-root/usr/share/polkit-1/actions/

	# Abitti Downloader scripts
	mkdir -p temp/deb-root/etc/cron.d
	cp downloader/abitti-downloader.cron temp/deb-root/etc/cron.d/abitti-downloader

	mkdir -p temp/deb-root/usr/local/sbin/
	cp downloader/abitti-downloader.sh temp/deb-root/usr/local/sbin/abitti-downloader

	mkdir -p temp/deb-root/etc/default/
	cp downloader/abitti-downloader.default temp/deb-root/etc/default/abitti-downloader

	echo -n ${VERSION_FULL} >temp/VERSION_FULL.tmp

	fpm -C temp/deb-root/ -s dir --name digabi-usb-monster --architecture all -t deb --version ${VERSION_FULL} \
	  --description "Digabi USB monster is a Python/Curses script used by Matriculation Examination board to write massive amount of USB sticks in short timeframe." \
	  --maintainer "abitti@ylioppilastutkinto.fi" \
	  --vendor "Matriculation Examination Board" \
	  --depends pv \
	  --depends python3 \
	  --depends python3-psutil \
	  --depends "terminator | xfce4-terminal" \
	  --depends zenity \
	  --depends unzip \
		--depends policykit-1 \
	  .
