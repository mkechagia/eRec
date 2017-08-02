#!/bin/bash

# download the android-platforms from the eRec-data repo
ANDROID_JARS_PATH="../../android-platforms/"
JAVA_CLASSPATH="\
../../soot-material/soot-trunk.jar:\
../../soot-material/baksmali-2.0.3.jar:\
../../soot-material/AXMLPrinter2:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"

APK_FILE=$1
SOOT_OUT_DIR=$2

# download some apk files to analyze into the ../eRec/apps/apk/ forlder
PROCESS_THIS=" -pp -process-dir $APK_FILE" 
SOOT_CLASSPATH="\
../../soot-material/soot-trunk.jar:\
../../soot-material/baksmali-2.0.3.jar:\
../../soot-material/AXMLPrinter2:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"${APK_FILE}":\
"
SOOT_CMD="soot.Main --soot-classpath $SOOT_CLASSPATH \
 -d $SOOT_OUT_DIR \
 -i android. \
 -android-jars $ANDROID_JARS_PATH \
 -allow-phantom-refs \
 -src-prec apk \
 -ire \
 -show-exception-dests \
 -annot-nullpointer \
 -annot-arraybounds \
 -xml-attributes \
 -f J \
 $PROCESS_THIS
"

# to increase JVM memory
java \
 -Xss50m \
 -Xmx1500m \
 -classpath  ${JAVA_CLASSPATH} \
 ${SOOT_CMD} \
 > $SOOT_OUT_DIR/soot_log.txt