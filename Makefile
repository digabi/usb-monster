clean-deb:
	- rm src/VERSION_FULL.tmp
	- rm src/*.deb

deb: src/* clean-deb
	cd src; sh create-deb.sh
