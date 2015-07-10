#!/bin/bash

version=`cat src/tpfanco_admin/build.py | grep "^version = " | sed  -e "s/version = \"\(.*\)\"/\1/"`
bzr export ../packages/tarballs/tpfanco-admin-${version}.tar.gz
cd ../packages/tarballs
ln -sf tpfanco-admin-${version}.tar.gz tpfanco-admin_${version}.orig.tar.gz

