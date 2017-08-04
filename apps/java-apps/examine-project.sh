#!/bin/bash

LIBRARIES=('apache' 'google')
BUILDFILES=('build.gradle' 'build.xml' 'pom.xml')

#echo "no of patterns: ${#LIBRARIES[@]}"
#echo "patterns: ${LIBRARIES[@]}"

p=0
for (( p = 0; p<${#LIBRARIES[@]} - 1; p++ ));
do
	REGEX+="${LIBRARIES[p]}|"
	#echo $REGEX
done

REGEX+="${LIBRARIES[p]}"

#echo $REGEX

find . -name "${BUILDFILES[0]}" \
	 -o -name "${BUILDFILES[1]}" \
	-o -name "${BUILDFILES[2]}" \
| xargs egrep "$REGEX"
