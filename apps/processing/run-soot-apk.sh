#!/bin/bash

sampledir=`pwd`
samplepath=../processing/runSootOnApk.sh

find $sampledir -type f -name \*.apk |
while read apk; do
  name=$(basename $apk .apk)
  mkdir -p $name
  $samplepath $apk $name 2>$name/errors.txt
done