import csv
import sys
import re
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests.auth import HTTPBasicAuth
import time
from os import path
from xml.sax.saxutils import escape
import traceback
import configparser

from cswaExtras import postxml, relationsPayload
from utils4groups import add2group, create_group

# NB: this is set in utils, but we cannot import that Django module in this ordinary script due to dependencies
FIELDS2WRITE = 'name size objectnumber date creator contributor rightsholder imagenumber handling approvedforweb'.split(' ')


def linkmedia(mediaElements, config, http_parms):

    messages = []
    objectCSID = mediaElements['objectCSID']
    mediaCSID = mediaElements['mediaCSID']
    uri = 'relations'

    #messages.append("posting media2obj to relations REST API...")
    mediaElements['objectCsid'] = objectCSID
    mediaElements['subjectCsid'] = mediaCSID
    # "urn:cspace:institution.cspace.berkeley.edu:media:id(%s)" % mediaCSID

    mediaElements['objectDocumentType'] = 'CollectionObject'
    mediaElements['subjectDocumentType'] = 'Media'

    payload = relationsPayload(mediaElements)
    (url, data, csid, elapsedtime1) = postxml('POST', uri, http_parms.realm, http_parms.server, http_parms.username, http_parms.password, payload)
    # elapsedtimetotal += elapsedtime
    #messages.append('relation media2obj csid %s elapsedtime %s ' % (csid, elapsedtime))
    mediaElements['media2objCSID'] = csid
    #messages.append("relations REST API post succeeded...")

    # reverse the roles
    #messages.append("posting obj2media to relations REST API...")
    temp = mediaElements['objectCsid']
    mediaElements['objectCsid'] = mediaElements['subjectCsid']
    mediaElements['subjectCsid'] = temp
    mediaElements['objectDocumentType'] = 'Media'
    mediaElements['subjectDocumentType'] = 'CollectionObject'
    payload = relationsPayload(mediaElements)
    (url, data, csid, elapsedtime2) = postxml('POST', uri, http_parms.realm, http_parms.server, http_parms.username, http_parms.password, payload)
    #messages.append('relation obj2media csid %s elapsedtime %s ' % (csid, elapsedtime))
    mediaElements['obj2mediaCSID'] = csid
    messages.append("REST API post for two relations succeeded, elapsedtime %8.2f s." % (elapsedtime1 + elapsedtime2))
    for m in messages:
        print("   %s" % m)
    return mediaElements


def getRecords(rawFile):
    try:
        f = open(rawFile, 'r', encoding='utf-8')
        csvfile = csv.reader(f, delimiter="|")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % rawFile
        return message, -1
    except:
        raise

    try:
        records = []
        for row, values in enumerate(csvfile):
            records.append(values)
        return records, len(values)
    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % rawFile
        return message, -1
    except:
        raise


if __name__ == "__main__":

    if len(sys.argv) == 3:
        print("MEDIA: input  file (fully qualified path): %s" % sys.argv[1])
        print("MEDIA: config file (fully qualified path): %s" % sys.argv[2])
    else:
        print()
        print("usage: %s <filename> <config file>" % sys.argv[0])
        print("e.g.   %s objandmediacsicd.csv pahma_Uploadmedia_dev.cfg" % sys.argv[0])
        print()
        sys.exit(1)

    try:
        config = configparser.RawConfigParser()
        config.read(sys.argv[2])
    except:
        print("MEDIA: could not get configuration from %s" % sys.argv[2])
        sys.exit(1)

    class http_parms:
        pass

    try:
        http_parms.realm = config.get('connect', 'realm')
        http_parms.hostname = config.get('connect', 'hostname')
        http_parms.port = config.get('connect', 'port')
        http_parms.protocol = config.get('connect', 'protocol')
        http_parms.username = config.get('connect', 'username')
        http_parms.password = config.get('connect', 'password')
        http_parms.institution = config.get('info', 'institution')

        http_parms.server = http_parms.protocol + "://" + http_parms.hostname

        try:
            int(http_parms.port)
            http_parms.server = http_parms.server  + ':' + http_parms.port
        except:
            pass

        http_parms.cache_path = config.get('files', 'directory')

    except:
        print("could not get at least one of realm, hostname, port, protocol, username, password or institution from config file.")
        print("can't continue, exiting...")
        sys.exit(1)

    records, columns = getRecords(sys.argv[1])
    if columns == -1:
        print('MEDIA: Error! %s' % records)
        sys.exit()

    print('MEDIA: %s columns and %s lines found in file %s' % (columns, len(records), sys.argv[1]))
    outputFile = sys.argv[1].replace('.csv', '-results.csv')
    outputfh = csv.writer(open(outputFile, 'w'), delimiter="|")

    # the first row of the file is a header
    columns = records[0]
    del records[0]
    outputfh.writerow(columns)

    # this list contains ONLY the csids of objects that had media related, if any
    objectCSIDs = []
    group_title = ''
    for i, r in enumerate(records):

        elapsedtimetotal = time.time()
        mediaElements = {}
        # ensure that all the possible fields have keys in this dict
        for v in FIELDS2WRITE:
            mediaElements[v] = ''
        # now insert the actual values for those that appear in the input
        for v1, v2 in enumerate(columns):
            mediaElements[v2] = r[v1]
            # snag group_title, if provided
            if v2 == 'group_title':
                if r[v1] == '=job':
                    group_title = sys.argv[1].split('.')[0]
                    group_title = group_title.split('/')[-1]
                    group_title = f'bmu-{group_title}'
                else:
                    group_title = r[v1]

        mediaElements['handling'] = 'xxx'
        print('MEDIA: uploading media for filename %s, objectnumber: %s' % (mediaElements['name'], mediaElements['objectnumber']))
        try:
            # mediaElements = uploadblob(mediaElements, config, http_parms)
            mediaElements = linkmedia(mediaElements, config, http_parms)
            print("MEDIA: objectnumber %s, objectcsid: %s, mediacsid: %s, %8.2f" % (
                mediaElements['objectnumber'], mediaElements['objectCSID'], mediaElements['mediaCSID'],
                (time.time() - elapsedtimetotal)))

            if not ('N/A' in mediaElements['objectCSID'] or 'not found' in mediaElements['objectCSID']):
                objectCSIDs.append(mediaElements['objectCSID'])

            outputfh.writerow(r)
        except:
            print("%s" % traceback.format_exc())
            print("MEDIA: create failed for blob or media. objectnumber %s, %8.2f s." % (
                mediaElements['objectnumber'], (time.time() - elapsedtimetotal)))
            # delete the blob if we did not manage to make a media record for it...
            try:
                (url, data, deletedCSID, elapsedtime) = postxml('DELETE', 'blobs/%s' % mediaElements['blobCSID'], http_parms.realm, http_parms.server, http_parms.username,
                                                          http_parms.password, '')
                print("MEDIA: deleted blob %s" % mediaElements['blobCSID'])
            except:
                try:
                    print("MEDIA: failed to delete blob %s" % mediaElements['blobCSID'])
                except:
                    pass

    # make a group, if asked
    if group_title != '':

        if len(objectCSIDs) > 0:
            groupCSID = create_group(group_title, http_parms)
            add2group(groupCSID, objectCSIDs, http_parms)
            print(f'GROUP: created group {group_title} (csid: {groupCSID}) with {len(objectCSIDs)} objects')
        else:
            print(f'GROUP: no group created {group_title}, there were no objects to group.')

