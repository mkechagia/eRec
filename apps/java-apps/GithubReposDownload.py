from github import Github
import os
from subprocess import call
import time
import random
import datetime
import re
import sys


def downloadRepo(outputPath, repoName, counter):
    fullRepoName = 'https://github.com/' + repoName + '.git'
    os.chdir(outputPath)
    folderName = repoName.replace("/", "_")
    if not os.path.isdir(os.path.join(outputPath, folderName)):
        print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + ' cloning: ', fullRepoName)
        os.mkdir(folderName)
        call(['git', 'clone', fullRepoName, folderName])
        call(['rm', '-rf', '%s/*' % folderName])
        n = random.randint(50,70)
        print('On repo No %d: waiting for %d secs' % (counter, n))
        time.sleep(n)

g = Github('testSDKGithub', 'Testing1!')
inputFilePath = sys.argv[1]
outputPath = sys.argv[2]
stars_threshold = int(sys.argv[3])
commits_threshold = int(sys.argv[4])
with open(inputFilePath, 'rt', errors='ignore') as f:
  lines = f.readlines()
counter = 0

for line in lines[1:]:
    match = re.search(r'https://api.github.com/repos/(.+),(\d+),(\d+)$', line)
    if match:
        repoName = match.group(1)
        stars = int(match.group(2))
        commits = int(match.group(3))
        if not repoName == '' \
           and stars >= stars_threshold \
           and commits >= commits_threshold:
            counter += 1
            downloadRepo(outputPath, repoName, counter)

