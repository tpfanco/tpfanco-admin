DESTDIR=/

all: man pofiles

pofiles:
	./compile_po.sh

man: tpfanco-admin.1

tpfanco-admin.1: man/tpfanco-admin.pod
	pod2man --section=1 --release=Version\ `cat src/tpfanco_admin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"` --center "" man/tpfanco-admin.pod > tpfanco-admin.1

clean:
	rm -f tpfanco-admin.1
	rm -f src/tpfanco_admin/*.pyc
	rm -rf mo

install: all
	install -d ${DESTDIR}/usr/share/pyshared/tpfanco_admin
	install -m 644 src/tpfanco_admin/* ${DESTDIR}/usr/share/pyshared/tpfanco_admin
	install -d ${DESTDIR}/usr/share/tpfanco-admin/
	install -m 644 share/* ${DESTDIR}/usr/share/tpfanco-admin/
	install -d ${DESTDIR}/usr/bin
	install -m 755 wrappers/tpfanco-admin ${DESTDIR}/usr/bin/
	install -d ${DESTDIR}/usr/share/tpfanco-admin/locales/
	cp -av mo/* ${DESTDIR}/usr/share/tpfanco-admin/locales/
	install -d ${DESTDIR}/usr/share/applications
	install -m 644 share/tpfanco-admin.desktop ${DESTDIR}/usr/share/applications

uninstall:
	rm -rf ${DESTDIR}/usr/share/pyshared/tpfanco_admin
	rm -rf ${DESTDIR}/usr/share/tpfanco-admin/
	rm -f ${DESTDIR}/usr/bin/tpfanco-admin
	rm -f ${DESTDIR}/usr/share/applications/tpfanco-admin.desktop


