#!/bin/bash

for file in po/tpfanco-admin-*.po ;
do
  newfile=`echo $file | sed -e 's/tpfanco-admin-//'`
  echo "$file -> $newfile"
  mv -f $file $newfile
done

