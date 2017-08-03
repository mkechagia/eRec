#!/bin/bash

### Don't forget to study the instructions.txt file first and provide the right inputs!
### Comment out the commands you don't want to execute! Otherwise, the analysis will take too long.
### May you will only need to run the set operations in the end of the script!
### Already processed data can be found in the eRec-data repo (https://github.com/mkechagia/eRec-data.git).

# Directory where the eRec repo is downloaded
cwd=`pwd`


### 1. API ###

### a) API documentation ###

# uncomment the following commands in case you want automatically unzip a Java API version in the sources folder
# you can also use the $cwd/api/processing/doc/sources/get_sources.sh script
#cd $cwd/api/processing/doc/sources/

# change the Java version (#) you want to analyze
#mkdir java-#
#cd java-#

# unzip the code of the JDK (provided by Oracle).
# Becareful of what Java version you have in your JAVA_HOME.
# If you want to unzip a different Java version (of your JAVA_HOME),
# you need to change the following path accordingly.
#unzip $JAVA_HOME/src.zip
# Note: for 3rd-pary Java libraries, download the source code of the library you want to analyze into the sources folder.

cd $cwd/api/processing/doc/doclet/

# - use sh or bash depending on your system
# - set the API version (where #) you want to analyze
sh $cwd/api/processing/doc/gen-doc.sh $cwd/api/processing/doc/sources/java-#/java/
# Note: change for 3rd-party Java libraries accordingly, e.g.:
#sh $cwd/api/processing/doc/gen-doc.sh $cwd/api/processing/doc/sources/commons-io-commons-io-2.5/src/main/java/

cd $cwd/api/JSON/

python $cwd/api/processing/doc/api_doc_exceptions.py $cwd/api/processing/doc/sources/ java
# Note: change for 3rd-party Java libraries accordingly, e.g.:
#python $cwd/api/processing/doc/api_doc_exceptions.py $cwd/api/processing/doc/sources/ org.apache.commons.io

### b) API source code ###

cd $cwd/api/JSON/

# replace "sample-app" with the jar to be analyzed and "XX" with the API version to be used
# one app for each API version is sufficient since Soot analyzes also the Java libraries used by an .jar.
# Note: for this step, you need to have run .jar analysis (see step 2. Apps) on specific Java projects
python $cwd/api/processing/source/api_source_code_exceptions.py $cwd/apps/jar/sample-app XX java
# e.g.: python $cwd/api/processing/source/api_source_code_exceptions.py $cwd/apps/jar/commons-lang3-3.4 8 java


### c) total API versions in .json file (one file for doc and one for source code) ###

cd $cwd/api/JSON/

python $cwd/api/processing/total_api_versions.py $cwd/api/JSON/ java
# Note: change for 3rd-party Java libraries accordingly, e.g.:
#python $cwd/api/processing/total_api_versions.py $cwd/api/JSON/ org.apache.commons.io


### 2. Apps ###

cd $cwd/apps/jar/

# use sh or bash depending on your system
sh $cwd/apps/processing/run-soot-jar.sh

cd ..

python $cwd/apps/processing/proj_exceptions.py $cwd/apps/jar/ $cwd/api/JSON/ 8 java #>> progress.log 2>>progress.err &
# Note: change for 3rd-party Java libraries accordingly, e.g.:
#python $cwd/apps/processing/proj_exceptions.py $cwd/apps/jar/ $cwd/api/JSON/ 2.5 org.apache.commons.io

# After some filtering of the $cwd/apps/java-undoc-excps.txt file,
# we can get the produced file $cwd/apps/java-undoc-excps-processed.txt; we provide such a sample file in the apps folder of the eRec-data.
# Note: for 3rd-party Java libraries we will get accordingly, e.g.:
#$cwd/apps/org.apache.commons.io-undoc-excps.txt

### 3. Crashes ###

# The way of the processing of the stack traces can be found in KMS15.
# We use the resulted signatures: $cwd/crashes/java-api-culprits.txt
# Note: for 3rd-party Java libraries we will have accordingly, e.g.:
#$cwd/crashes/org.apache.commons.io-api-culprits.txt


### Set operations ###

cd $cwd

# check the four parameters for the following python script
python $cwd/set-operations/api_sc_doc_apps_st_total.py $cwd/api/JSON/total_versions_java.json $cwd/api/JSON/total_versions_sc_java.json $cwd/apps/java-undoc-excps-processed.txt $cwd/crashes/java-api-culprits.txt java
# Note: for 3rd-party Java libraries we will have accordingly, e.g.:
#python $cwd/set-operations/api_sc_doc_apps_st_total.py $cwd/api/JSON/total_versions_org.apache.commons.io.json $cwd/api/JSON/total_versions_sc_org.apache.commons.io.json $cwd/apps/org.apache.commons.io-undoc-excps-processed.txt $cwd/crashes/org.apache.commons.io-api-culprits.txt java