#!/usr/bin/env python3

import argparse
import configparser
import os
import sys
import adba

stateToUDP = dict(unknown=0, hdd=1, cd=2, deleted=3)
viewedToUDP = dict(unwatched=0, watched=1)
blacklistFields = list(('unused', 'retired', 'reserved', 'IsDeprecated'))
fileTypes = '.avi,.mp4,.mkv,.ogm'

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['hash', 'mylistadd', 'mylistdel', 'mylistaddwithfields', 'getfields', 'listfields', 'logout'],
help='Command to execute. hash: Hash the file and print its ed2k hash. mylistadd: Hash the file and add it to AniDB MyList. If the file was there, it will be updated. mylistdel: Hash the file and delete it from AniDB MyList. getfields: Hash the file and retrieve requested fields for the hashed file. listfields: Lists all the available fields that can be requested from AniDB.')
parser.add_argument('file', nargs='*', default=[],
help='All file(s) and/or folder(s) to be processed.')
parser.add_argument('--file-types', default=fileTypes,
help='A comma delmited list of file types to be included when searching directories. Default: ' + fileTypes)
parser.add_argument('--out-file',
help='Write output to specified file instead of STDOUT.')
parser.add_argument('-u', '--username',
help='User name needed to communicate with AniDB.')
parser.add_argument('-p', '--password',
help='Password needed to communicate with AniDB.')
parser.add_argument('-l', '--login',
help='Login credentials ini file to login to AniDB.')
parser.add_argument('--state', choices=['unknown', 'hdd', 'cd', 'deleted'], default='hdd',
help='Sets the file state to unknown/hdd/cd/deleted. Default: hdd')
parser.add_argument('--watched', action='store_true',
help='Marks the file as watched.')
parser.add_argument('--unwatched', action='store_true',
help='Marks the file as unwatched.')
parser.add_argument('--source',
help='Sets the file source (any string).')
parser.add_argument('--storage',
help='Sets file storage (any string).')
parser.add_argument('--other',
help='Sets other remarks (any string).')
parser.add_argument('--fields',
help='A comma delimited list of fields requested from AniDB.')
parser.add_argument('--wait-input', action='store_true',
help='Wait for user input before exiting the script.')
parser.add_argument('--fast-command-delay', action='store_true',
help='Specify the command delay to wait for 2.1 seconds as opposed to the default of 4.1 seconds.')
parser.add_argument('--logging', action='store_true',
help='Enable debug level logging to file.')

args = parser.parse_args()

if args.login:
	# Extract the login credentials
	config = configparser.ConfigParser()
	try:
		config.read(args.login)
		args.username = config['DEFAULT']['user']
		args.password = config['DEFAULT']['password']
	except Exception as e:
		print('Exception:', e)
		input("Press Enter to continue")
		sys.exit(1)

if args.logging:
	# Start logging
	FileListener = adba.StartLogging()

if args.out_file:
	sys.stdout = open(args.out_file, 'w', encoding='UTF-8')

# Issue logout of session
if args.command == 'logout':
	connection = adba.Connection(commandDelay=2.1)
	connection.logout()
	input("Press Enter to continue")
	sys.exit(0)

# Check if fields are required
if args.command in ['mylistaddwithfields', 'getfields']:
	if not args.fields:
		print("Fields to retrieve are required for " + args.command + ".")
		input("Press Enter to continue")
		sys.exit(0)

# Convert state to UDP
if args.command == 'mylistdel':
	args.state = stateToUDP['deleted']
else:
	args.state = stateToUDP[args.state]

# Convert watched to UDP
if args.watched:
	viewed = viewedToUDP['watched']
elif args.unwatched:
	viewed = viewedToUDP['unwatched']
else:
	viewed = None

# Parse positional arguments passed in and convert all to files
fileList = list()
validExtensions = args.file_types.lower().split(',')
for entry in list(args.file):
	if os.path.isfile(entry):
		if any(os.path.splitext(entry)[1].lower() == valid for valid in validExtensions):
			fileList.append(entry)
	elif os.path.isdir(entry):
		for dirpath, dirnames, filenames in os.walk(entry):
			for filename in filenames:
				if any(os.path.splitext(filename)[1].lower() == valid for valid in validExtensions):
					fileList.append(os.path.normpath(dirpath + os.sep + filename))

# Check if files are required
if args.command in ['hash', 'mylistadd', 'mylistdel', 'mylistaddwithfields', 'getfields']:
	if len(fileList) == 0:
		print("Files and/or directories containing valid files are required for " + args.command + ".")
		input("Press Enter to continue")
		sys.exit(0)

# Check if login is required and create connection if have login credentials
if args.command in ['mylistadd', 'mylistdel', 'mylistaddwithfields', 'getfields']:
	if not args.username or not args.password:
		print("User and password required for " + args.command + ".")
		input("Press Enter to continue")
		sys.exit(0)
	if args.fast_command_delay:
		connection = adba.Connection(commandDelay=2.1)
	else:
		connection = adba.Connection()
	try:
		connection.auth(args.username, args.password)
	except Exception as e:
		print('Exception:', e)

# Execute command
if args.command == 'hash':
	# Hash the file
	for thisFile in fileList:
		thisED2K = adba.aniDBfileInfo.get_ED2K(thisFile, forceHash=True)
		print(thisED2K)
elif args.command == 'mylistadd':
	# First try to add the file, then try to edit
	if connection.authed():
		for thisFile in fileList:
			try:
				episode = adba.Episode(connection, filePath=thisFile)
			except Exception as e:
				print('Exception:', e)
				continue
			try:
				episode.edit_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
				print(os.path.basename(thisFile) + " successfully edited in AniDB MyList.")
			except:
				try:
					episode.add_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
					print(os.path.basename(thisFile) + " successfully added to AniDB MyList.")
				except Exception as e:
					print('Exception:', e)
					continue
elif args.command == 'mylistdel':
	# Delete the file
	if connection.authed():
		for thisFile in fileList:
			try:
				episode = adba.Episode(connection, filePath=thisFile)
			except Exception as e:
				print('Exception:', e)
				continue
			try:
				episode.edit_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
				print(os.path.basename(thisFile) + " successfully edited as deleted from AniDB MyList.")
			except Exception as e:
				try:
					episode.add_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
					print(os.path.basename(thisFile) + " successfully added as deleted to AniDB MyList.")
				except Exception as e:
					print('Exception:', e)
					continue
elif args.command == 'mylistaddwithfields':
	# Parse requested field(s)
	requestedFields = list(args.fields.lower().split(','))
	# Separate fields by request type
	maper = adba.aniDBmaper.AniDBMaper()
	maperFileF = set(maper.getFileMapF())
	maperFileA = set(maper.getFileMapA())
	requestF = list(maperFileF & set(requestedFields))
	requestA = list(maperFileA & set(requestedFields))
	# Add/edit the file to AniDB and print the retrieved field(s)
	if connection.authed():
		for thisFile in fileList:
			try:
				episode = adba.Episode(connection, filePath=thisFile, load=True, paramsF=requestF, paramsA=requestA)
			except Exception as e:
				print('Exception:', e)
				continue
			try:
				episode.edit_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
				print(os.path.basename(thisFile) + " successfully edited in AniDB MyList.")
			except:
				try:
					episode.add_to_mylist(state=args.state, viewed=viewed, source=args.source, storage=args.storage, other=args.other)
					print(os.path.basename(thisFile) + " successfully added to AniDB MyList.")
				except Exception as e:
					print('Exception:', e)
					continue
			print("filename\t" + thisFile)
			for field in requestedFields:
				print(field + "\t" + str(getattr(episode, field)))
			print("")
elif args.command == 'getfields':
	# Parse requested field(s)
	requestedFields = list(args.fields.lower().split(','))
	# Separate fields by request type
	maper = adba.aniDBmaper.AniDBMaper()
	maperFileF = set(maper.getFileMapF())
	maperFileA = set(maper.getFileMapA())
	requestF = list(maperFileF & set(requestedFields))
	requestA = list(maperFileA & set(requestedFields))
	# Retrieve the requested field(s)
	if connection.authed():
		for thisFile in fileList:
			try:
				episode = adba.Episode(connection, filePath=thisFile, load=True, paramsF=requestF, paramsA=requestA)
			except Exception as e:
				print('Exception:', e)
				continue
			print("filename\t" + thisFile)
			for field in requestedFields:
				print(field + "\t" + str(getattr(episode, field)))
			print("")
elif args.command == 'listfields':
	# Print all the possible field(s) that can be requested, remove blacklisted fields
	maper = adba.aniDBmaper.AniDBMaper()
	maperFileF = list(maper.getFileMapF())
	maperFileA = list(maper.getFileMapA())
	allFields = maperFileF + maperFileA
	validFields = sorted([field for field in allFields if field not in blacklistFields])
	print('\n'.join(validFields))

connection.stayloggedin()

if args.out_file:
	sys.stdout.close()

if (args.logging):
	adba.StopLogging(FileListener)

if args.wait_input:
	input("Press Enter to continue")
sys.exit(0)
