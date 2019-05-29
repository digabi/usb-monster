DD_CURSES_VERSION := $(shell cat dd-curses/VERSION)
DD_DEB=digabi-dd-curses_$(DD_CURSES_VERSION)_all.deb

clean-deb:
	rm dd-curses/*.deb

clean-repo:
	rm -fR docs/debian/db/
	rm -fR docs/debian/dists/
	rm -fR docs/debian/pool/

dd-curses/$(DD_DEB): dd-curses/*
	cd dd-curses; sh create-deb.sh

update-repo-deb: dd-curses/$(DD_DEB)
	reprepro -b docs/debian includedeb stable dd-curses/$(DD_DEB)
