DESTDIR=/

all: man pofiles

pofiles:
	./compile_po.sh

man: tpfanco-admin.1

tpfanco-admin.1: man/tpfanco-admin.pod
	pod2man --section=1 --release=Version\ `cat src/tpfanco_admin.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"` --center "" man/tpfanco-admin.pod > tpfanco-admin.1

clean:
	rm -f tpfanco-admin.1
	rm -f src/tpfanco_admin/*.pyc
	rm -rf mo

install: all
	install -d ${DESTDIR}/usr/lib/python2.7/site-packages/tpfanco_admin
	install -m 644 src/tpfanco_admin/* ${DESTDIR}/usr/lib/python2.7/site-packages/tpfanco_admin
	install -d ${DESTDIR}/usr/share/tpfanco-admin/
	install -m 644 share/*.png ${DESTDIR}/usr/share/tpfanco-admin/
	install -m 644 share/*.svg ${DESTDIR}/usr/share/tpfanco-admin/
	install -m 644 share/*.glade ${DESTDIR}/usr/share/tpfanco-admin/
	install -d $(DESTDIR)/usr/share/polkit-1
	install -d $(DESTDIR)/usr/share/polkit-1/actions
	install -m 644 share/polkit-1/actions/org.tpfanco.tpfanco-admin.policy $(DESTDIR)/usr/share/polkit-1/actions/org.tpfanco.tpfanco-admin.policy

	install -d ${DESTDIR}/usr/bin
	install -m 755 src/tpfanco-admin.py ${DESTDIR}/usr/bin/tpfanco-admin
	install -m 755 src/tpfanco-admin_polkit ${DESTDIR}/usr/bin/tpfanco-admin_polkit
	install -d ${DESTDIR}/usr/share/tpfanco-admin/locales/
	install -d ${DESTDIR}/usr/share/applications
	install -m 644 share/tpfanco-admin.desktop ${DESTDIR}/usr/share/applications

uninstall:
	rm -rf ${DESTDIR}/usr/lib/python2.7/site-packages/tpfanco_admin
	rm -rf ${DESTDIR}/usr/share/tpfanco-admin/
	rm -f ${DESTDIR}/usr/bin/tpfanco-admin
	rm -f ${DESTDIR}/usr/bin/tpfanco-admin_polkit
	rm -f ${DESTDIR}/usr/share/applications/tpfanco-admin.desktop
	rm -f $(DESTDIR)/usr/share/polkit-1/actions/org.tpfanco.tpfanco-admin.policy


