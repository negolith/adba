#!/usr/bin/env python
# coding=utf-8
#
# This file is part of aDBa.
#
# aDBa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aDBa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with aDBa.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os
import getopt
import pickle
from test_lib import *
from adba.aniDBfileInfo import *

####################################################
# here starts the stuff that is interresting for you
####################################################

# you only need to import the module
import adba

# lets see the version
print("Version:", adba.version)
# print(sys.executable)

# first part of this code if proof of concept for hashing files into the pickle and testing efficiency of calling pickle
# should be commented out in general

# takes a root directory and recursively hashes all files and stores them in the cache
# subsequent runs should be very fast
testRootDir = sys.argv[1]

fileCount = 0
filesToHash = 400
ED2KCache = {}
for dirPath, dirNames, fileNames in os.walk(testRootDir):
    for fileName in fileNames:
        currentFilePath = os.path.normpath(dirPath + os.sep + fileName)
        eD2KHash = get_ED2K(currentFilePath)
        print(currentFilePath, eD2KHash)
        ED2KCache[fileName] = eD2KHash
        fileCount += 1
        if fileCount > filesToHash:
            break
    if fileCount > filesToHash:
        break

for key in ED2KCache:
    print(key, ED2KCache[key])

print(len(ED2KCache))
