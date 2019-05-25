DD_CURSES_VERSION := $(shell cat dd-curses/VERSION)
DD_DEB=digabi-dd-curses_$(DD_CURSES_VERSION)_all.deb

clean:
	rm dd-curses/*.deb
	
dd-curses/$(DD_DEB): dd-curses/*
	cd dd-curses; sh create-deb.sh
	
update-repo-deb: dd-curses/$(DD_DEB)
	reprepro -b docs/debian includedeb stable dd-curses/$(DD_DEB) 
