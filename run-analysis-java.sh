#!/bin/bash

### Don't forget to study the README.md file first and provide the right inputs!
### Comment out the commands you don't want to execute!
### May you will need only the set operations in the end!

# Directory where the eRec repo is downloaded
cwd=`pwd`


### 1. API ###

### a) API documentation ###

cd $cwd/api/processing/doc/sources/

# change the Java version (#) you want to analyze
#mkdir java-#
#cd java-#

# unzip the code of the JDK (provided by Oracle).
# Becareful of what Java version you have in your JAVA_HOME.
# If you want to unzip a different Java version (of your JAVA_HOME),
# you need to change the following path accordingly.
#unzip $JAVA_HOME/src.zip

cd $cwd/api/processing/doc/doclet/

# - use sh or bash depending on your system
# - set the API version (where #) you want to analyze
sh $cwd/api/processing/doc/gen-doc.sh $cwd/api/processing/doc/sources/java-#/java/

cd $cwd/api/JSON/

python $cwd/api/processing/doc/api_doc_exceptions.py $cwd/api/processing/doc/sources/ java

### b) API source code ###

cd $cwd/api/JSON/

# replace "sample-app" with the app to be analyzed and "XX" with the API version of the app --- one app for each API version
python $cwd/api/processing/source/api_source_code_exceptions.py $cwd/apps/jar/sample-app XX java


### c) total API versions in .json file (one file for doc and one for source code) ###

cd $cwd/api/JSON/

python $cwd/api/processing/total_api_versions.py $cwd/api/JSON/ java


### 2. Apps ###

cd $cwd/apps/jar/

# use sh or bash depending on your system
sh $cwd/apps/processing/run-soot-jar.sh

cd ..

python $cwd/apps/processing/proj_exceptions.py $cwd/apps/jar/ $cwd/api/JSON/ 8 java #>> progress.log 2>>progress.err &

# After some filtering of the $cwd/apps/undoc_exc.txt file,
# we can get the produced file $cwd/apps/api_exc_valid_uniq_undoc_new_orig.txt
# awk -F ":" '{print $4 ":" $5}' ../eRec/apps/undoc_excps.txt | sort | uniq -c | sort -r > undoc_all.txt


### 3. Crashes ###

# The way of the processing of the stack traces can be found in KMS15.
# We provide the resulted processed (masked) signatures in: $cwd/crashes/api-culprits-total-new-3.txt
# awk '$2 ~ /^(java)\./' ../eRec/crashes/api-culprits-total.txt | awk -F ":" '{print $1 $2 $3 $4}' | sort -r > java_apis.txt
# awk '$2 ~ /^(java)\./' /Users/marki/Desktop/eRec_v3/crashes/api-culprits-total.txt | awk '{print $1",",$2",",$3",",$4}' > /Users/marki/Desktop/eRec_v3/java_a.txt

### Set operations ###

cd $cwd

# check the four parameters for the following python script
python $cwd/set-operations/api_sc_doc_apps_st_total.py $cwd/api/JSON/total_versions_java.json $cwd/api/JSON/total_versions_sc_java.json $cwd/apps/java-undoc-excps-processed.txt $cwd/crashes/java-api-culprits.txt java