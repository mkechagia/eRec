#!/bin/bash

# Data folder (TODO: add sample apk file)
if ! [ -d 'data' ]; then
	mkdir data
fi
if ! [ -d 'data/out' ]; then
	mkdir data/out
fi

if ! [ -d 'libs' ]; then
	mkdir libs
fi
cd libs

# Java 1.7 and Python 2.7
#sudo apt-get install -y openjdk-7-jdk openjdk-7-jre python2.7 git wget

if ! [ -f 'baksmali-2.0.3.jar' ]; then
	wget https://bitbucket.org/JesusFreke/smali/downloads/baksmali-2.0.3.jar
fi

# Android
if ! [ -f 'android-sdk_r23-linux.tgz' ]; then
	wget http://dl.google.com/android/android-sdk_r23-linux.tgz
fi
if ! [ -d 'android-sdk-linux' ]; then
	tar -xvf android-sdk_r23-linux.tgz
	cd android-sdk-linux/tools
	# Type 'y' to accept the license agreement (no -y flag unfortunately)
	./android update sdk --no-ui -a -t 'android-14,android-15,android-16,android-17,android-18,
				android-19,android-20,android-21,android-22,android-23'
fi

#  Set paths
#echo 'export PATH=$PATH:/opt/android-sdk-linux/platform-tools' >> /etc/profile.d/android.sh
#echo 'export ANDROID_TOOLS=/opt/android-sdk-linux' >> /etc/profile.d/android.sh
#source /etc/profile.d/android.sh
#  Install sdks
#cd /opt/android-sdk-linux/tools
#./android list sdk --all
#./android update -u -t 1,2,4,26,103

