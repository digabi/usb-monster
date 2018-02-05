APPNAME = usb-monster

all:

install:
	install -d -m 0755 $(DESTDIR)/usr/share/$(APPNAME)
	install -D -m 0755 write_dd.py $(DESTDIR)/usr/share/$(APPNAME)
	install -D -m 0755 ok.wav $(DESTDIR)/usr/share/$(APPNAME)
	install -D -m 0755 error.wav $(DESTDIR)/usr/share/$(APPNAME)

	cp lib/* ${DESTDIR}/usr/share/${APPNAME}/

	install -D -m 0644 udev/99-usbmonster.rules /etc/udev/rules.d
	install -D -m 0755 sbin/usbmonster-notifier /usr/local/sbin

uninstall:
	rm -fR $(DESTDIR)/usr/share/$(APPNAME)
	rm /etc/udev/rules.d/99-usbmonster.rules
	rm /usr/local/sbin/usbmonster-notifier
