#!/bin/bash

# set the $JAVA_HOME correctly!
javac -cp $JAVA_HOME/lib/tools.jar:. Tags.java

for var in $(find $1 -type f -iname "*.java"); do javadoc -sourcepath $1 -doclet Tags -docletpath .- ${var} > ${var}doc.txt; done