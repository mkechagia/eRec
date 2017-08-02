# Description: This script will help you to store in this folder
# the source code of the different versions of the APIs you want to analyze.
# For instance, if you want to analyze the Java API, you can store different versions
# of the API in folders such as: java-7, java-8, ect.
# So, if you want to analyze the Java API version 8 from Oracle,
# you can simply run the following commands. Where cwd represents the path
# where you have downloaded the eRec repo and JAVA_HOME should be defined in your bash profile.
#Carefully, change the paths for other APIs you want to analyze.

# How to run: sh $cwd/api/processing/doc/sources/get_sources.sh X
# X is the version of the Java API and cwd where the eRec repo is downloaded.

cwd=`pwd`

cd $cwd/api/processing/doc/sources/

mkdir java-$1
cd java-$1

# unzip the code of the JDK (provided by Oracle)
unzip $JAVA_HOME/src.zip

# After you have downloaded the sources you may want to export the path of the sources of the Java API in your bash profile.
#export JAVA=$cwd/eRec/api/processing/doc/sources/

# source ~/.bash_profile or ~/.profile
