#!/bin/bash

### Don't forget to study the instructions.txt file first and provide the right inputs!
### Comment out the commands you don't want to execute! Otherwise, the analysis will take too long.
### May you will only need to run the set operations in the end of the script!
### Already processed data can be found in the eRec-data repo (https://github.com/mkechagia/eRec-data.git).

# get the directory where the eRec repo is downloaded
cwd=`pwd`


### 1. API ###

### a) API documentation ###

cd $cwd/api/processing/doc/doclet/

# - use sh or bash depending on your system
# - set $ANDROID in your profile; it is where you have downloaded the Android platform, e.g. /../Programs/android/sdk/
# - set the API version (where #) you want to analyze
sh $cwd/api/processing/doc/gen-doc.sh $ANDROID/sources/android-#/android/

cd $cwd/api/JSON/

python $cwd/api/processing/doc/api_doc_exceptions.py $ANDROID/sources/ android

### b) API source code ###

cd $cwd/api/JSON/

# replace "sample-app" with the app to be analyzed and "XX" with the API version of the app;
# one app for each API version is sufficient since Soot (using Dexpler) analyzes also the Android libraries used by an .apk.
# Note: for this step, you need to provide the android-platforms and have run .apk analysis (see step 2. Apps) on specific apps
python $cwd/api/processing/source/api_source_code_exceptions.py $cwd/apps/apk/sample-app XX android

### c) total API versions in .json file (one file for doc and one for source code) ###

cd $cwd/api/JSON/

# this command will take some time depending on the number of API versions you want to analyze
# prepared .json files can be found in the eRec-data repo in the JSON directory
python $cwd/api/processing/total_api_versions.py $cwd/api/JSON/ android


### 2. Apps ###

cd $cwd/apps/apk/

# use sh or bash depending on your system
sh $cwd/apps/processing/run-soot-apk.sh

cd ..

python $cwd/apps/processing/app_exceptions.py $cwd/apps/apk/ $cwd/api/JSON/

# After some filtering of the $cwd/apps/android-undoc-excps.txt file,
# we can get the produced file $cwd/apps/android-undoc-excps-processed.txt; we provide such a sample file in the apps folder of the eRec-data.


### 3. Crashes ###

# The way of the processing of the stack traces can be found in KMS15.
# We use the resulted signatures: $cwd/crashes/android-api-culprits.txt


### Set operations ###

cd $cwd

# check the four parameters for the following python script
python $cwd/set-operations/api_sc_doc_apps_st_total.py $cwd/api/JSON/total_versions_android.json $cwd/api/JSON/total_versions_sc_android.json $cwd/apps/android-undoc-excps-processed.txt $cwd/crashes/android-api-culprits.txt android