#!/usr/bin/env python3
# coding=utf-8
import argparse
import os
import sys
import adba

relIDtoRelation = {1: "sequel", 2: "prequel", 11: "same setting", 12: "alternative setting", 32: "alternative version",
                   41: "music video", 42: "character", 51: "side story", 52: "parent story", 61: "summary", 62: "full story",
                   100: "other"}
relIDtoRelation = {key: 'relation-' + value for key, value in relIDtoRelation.items()}
blacklistFields = list(('unused', 'retired', 'reserved', 'IsDeprecated', 'category_list', 'category_weight_list', 'category_id_list', 'creator_id_list', 'character_id_list'))

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['animeinfo', 'logout'], help='Get info or log out')
parser.add_argument('AID', help='AID of Series wishing to find info for')
parser.add_argument('--out-file', action='store', default=None, help='Write output to specified file instead of STDOUT.')
parser.add_argument('-u', '--username', action='store', default=None, help='User name needed to communicate with AniDB.')
parser.add_argument('-p', '--password', action='store', default=None, help='Password needed to communicate with AniDB.')
args = parser.parse_args()

# Start logging
FileListener = adba.StartLogging()

if args.out_file:
    sys.stdout = open(args.out_file, 'w', encoding='UTF-8')

# Issue logout of session
if args.command == 'logout':
    connection = adba.Connection(commandDelay=2.1)
    connection.logout()
    print('Logged Out')
    sys.exit(0)

# we now need to login to actually get the anime info

connection = adba.Connection()

try:
    connection.auth(args.username, args.password)
except Exception as e:
    print('Exception: %s', e)
    sys.exit(1)

if connection.authed():
    try:
        maper = adba.aniDBmaper.AniDBMaper()
        animeFieldsWanted = maper.getAnimeMapA()
        # animeFieldsWanted=animeFieldsWanted[0:-1]
        animeMaper = [field for field in animeFieldsWanted if field not in blacklistFields]
        # print(animeFieldsWanted)
        animeInfo = adba.Anime(connection, aid=args.AID, load=True, paramsA=animeMaper)
        # print(animeInfo.rawData)
        for field in animeMaper:
            if field == 'related_aid_list':
                relatedDict = {value: "" for key, value in relIDtoRelation.items()}

                relatedAids = getattr(animeInfo, field)
                relatedAidTypes = getattr(animeInfo, 'related_aid_type')
                try:
                    for i in range(len(relatedAids)):
                        curID = relatedAids[i]
                        curRelation = relIDtoRelation[relatedAidTypes[i]]
                        if relatedDict[curRelation] == "":
                            relatedDict[curRelation] = str(curID)
                        else:
                            relatedDict[curRelation] = ",".join([relatedDict[curRelation], str(curID)])
                except:
                    relatedDict[relIDtoRelation[relatedAidTypes]] = relatedAids
                for key in relatedDict:
                    if relatedDict[key] != "":
                        print(key + '\t' + str(relatedDict[key]))
            elif field == 'related_aid_type':
                continue
            else:
                print(field + '\t' + str(getattr(animeInfo, field)))
                # print(getattr(animeInfo,'related_aid_list'))
    except Exception as e:
        connection.stayloggedin()
        print('Exception: %s', e)
        raise
        sys.exit(1)

# some clean up tasks that must happen every time
connection.stayloggedin()
adba.StopLogging(FileListener)
