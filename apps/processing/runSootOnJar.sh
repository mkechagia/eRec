#!/bin/bash

JAVA_CLASSPATH="\
../../soot-material/soot-trunk.jar:\
../../soot-material/baksmali-2.0.3.jar:\
../../soot-material/AXMLPrinter2:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"

JAR_FILE=$1
SOOT_OUT_DIR=$2

PROCESS_THIS=" -pp -process-dir $JAR_FILE" 
SOOT_CLASSPATH="\
../../soot-material/soot-trunk.jar:\
../../soot-material/baksmali-2.0.3.jar:\
../../soot-material/AXMLPrinter2:\
$JAVA_HOME/jre/lib/rt.jar:\
$JAVA_HOME/jre/lib/jsse.jar:\
$JAVA_HOME/jre/lib/jce.jar:\
"${JAR_FILE}":\
"

SOOT_CMD="soot.Main --soot-classpath $SOOT_CLASSPATH \
 -d $SOOT_OUT_DIR \
 -allow-phantom-refs \
 -show-exception-dests \
 -f J \
 $PROCESS_THIS
"
# You can instruct Soot to analyze more 3rd-party libraries
# by using the -include XX command above;
# where XX is the 3rd-party library to be analyzed
# -i java\
# -include org.apache.\
# -include org.w3c. \

# to increase JVM memory
java \
 -Xss50m \
 -Xmx1500m \
 -classpath  ${JAVA_CLASSPATH} \
 ${SOOT_CMD} \
 > $SOOT_OUT_DIR/soot_log.txt