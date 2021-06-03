DD_CURSES_VERSION := $(shell cat src/VERSION)
DD_DEB=digabi-dd-curses_$(DD_CURSES_VERSION)_all.deb

clean-deb:
	rm src/*.deb

clean-repo:
	rm -fR docs/debian/db/
	rm -fR docs/debian/dists/
	rm -fR docs/debian/pool/

src/$(DD_DEB): src/*
	cd src; sh create-deb.sh

update-repo-deb: src/$(DD_DEB)
	reprepro -b docs/debian includedeb stable src/$(DD_DEB)
