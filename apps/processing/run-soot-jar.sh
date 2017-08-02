#!/bin/bash

sampledir=`pwd`
samplepath=../processing/runSootOnJar.sh

find $sampledir -type f -name \*.jar |
while read jar; do
  name=$(basename $jar .jar)
  mkdir -p $name
  $samplepath $jar $name 2>$name/errors.txt
done