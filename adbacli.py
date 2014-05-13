#!/usr/bin/env python

import argparse
import logging
import os
import sys
import adba
import pprint

stateToUDP = dict(unknown=0, hdd=1, cd=2, deleted=3)
blacklistFields = list(('unused', 'retired', 'reserved'))

parser = argparse.ArgumentParser()
parser.add_argument('command', nargs=1, choices=['hash', 'mylistadd', 'getfields', 'listfields'],
help='Command to execute. hash: Hash the file and print its ed2k hash. mylistadd: Hash the file and add it to AniDB. If the file was there, it will be updated. getfields: Hash the file and retrieve requested fields for the hashed file. listfields: Lists all the available fields that can be requested from AniDB.')
parser.add_argument('args', nargs=argparse.REMAINDER,
help='All files and/or folders to be processed.')
parser.add_argument('--file-types', default='.avi,.mp4,.mkv,.ogv,.rmbv',
help='A comma delmited list of file types to be included when searching directories.')
parser.add_argument('--out-file', action='store',
help='Write output to specified file instead of STDOUT.')
parser.add_argument('-u', '--user', action='store', required=True,
help='User name needed to communicate with AniDB.')
parser.add_argument('-p', '--password', action='store', required=True,
help='Password needed to communicate with AniDB.')
parser.add_argument('--state', choices=['unknown', 'hdd', 'cd', 'deleted'], default='hdd',
help='Sets the file state to unknown/hdd/cd/deleted.')
parser.add_argument('--watched', action='store_true',
help='Marks the file as watched.')
parser.add_argument('--watchdate', action='store',
help='Sets the date the file was watched.')
parser.add_argument('--source', action='store',
help='Sets the file source (any string).')
parser.add_argument('--storage', action='store',
help='Sets file storage (any string).')
parser.add_argument('--other', action='store',
help='Sets other remarks (any string).')
parser.add_argument('--file-fields', action='store',
help='A comma delimited list of file fields requested from AniDB.')
parser.add_argument('--anime-fields', action='store',
help='A comma delimited list of anime fields requested from AniDB.')

args = parser.parse_args()

# Convert state to UDP
args.state = stateToUDP[args.state]

# Redirect sys.stdout if requested
if args.out_file:
	sys.stdout = open(args.out_file, 'w')

# Parse positional arguments passed in and convert all to files
fileList = list()
validExtensions = args.file_types.lower().split(',')
for entry in list(args.args):
	if os.path.isfile(entry):
		if any(os.path.splitext(entry)[1].lower() == valid for valid in validExtensions):
			fileList.append(entry)
	elif os.path.isdir(entry):
		for dirpath, dirnames, filenames in os.walk(entry):
			for filename in filenames:
				if any(os.path.splitext(filename)[1].lower() == valid for valid in validExtensions):
					fileList.append(filename)

if args.command[0] in ['mylistadd', 'getfields']:
	connection = adba.Connection(log=False)
	try:
		connection.auth(args.user, args.password)
	except Exception as e :
		print(("exception msg: "+str(e)))

if args.command[0] == 'hash':
	# Hash the file
	for thisFile in fileList:
		thisED2K = adba.aniDBfileInfo.get_ED2K(thisFile, forceHash=True)
		print(thisED2K)
#elif args.command[0] == 'mylistadd':
#	# First try to add the file, then try to edit
#	if connection.authed():
#		for thisFile in fileList:
#			episode = adba.Episode(connection, filePath=thisFile)
#			try:
#				episode.my_list_edit(status=args.state)
#			except:
#				episode.my_list_add(status=args.state)
#elif args.command[0] == 'getfields':
#	# Retrieve the requested fields
#	sys.exit(0)
elif args.command[0] == 'listfields':
	# Print all the possible fields that can be requested, remove blacklisted fields
	maper = adba.aniDBmaper.AniDBMaper()
	maperFileF = list(maper.getFileMapF())
	maperFileA = list(maper.getFileMapA())
	allFields = maperFileF + maperFileA
	validFields = [field for field in allFields if field not in blacklistFields]
	print('\t'.join(validFields))

if args.command[0] in ['mylistadd', 'getfields']:
	connection.logout(True)
sys.exit(0)