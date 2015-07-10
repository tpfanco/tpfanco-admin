#!/bin/bash

mkdir -p mo
cd po
for pofile in *.po
do
  lang=`echo $pofile | cut -d "." -f 1`
  mkdir -p ../mo/$lang/LC_MESSAGES/
  msgfmt -o ../mo/$lang/LC_MESSAGES/tpfanco-admin.mo $pofile
done


