DD_CURSES_VERSION := $(shell cat src/VERSION)
DD_DEB=digabi-dd-curses_$(DD_CURSES_VERSION)_all.deb

clean-deb:
	- rm src/VERSION_FULL.tmp
	- rm src/*.deb

clean-repo:
	rm -fR docs/debian/db/
	rm -fR docs/debian/dists/
	rm -fR docs/debian/pool/

deb: src/* clean-deb
	cd src; sh create-deb.sh

update-repo-deb: deb
	reprepro -b docs/debian includedeb stable src/$(DD_DEB)
