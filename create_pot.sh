#!/bin/bash

version=`cat src/tpfanco_admin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"`

options="--foreign-user --package-name=tpfanco-admin --package-version=${version} --msgid-bugs-address=surban84@googlemail.com  --copyright-holder=Sebastian_Urban -d tpfanco-admin -o po/tpfanco-admin.pot"

xgettext $options src/tpfanco_admin/*.py
xgettext $options -j share/tpfanco-admin.glade

