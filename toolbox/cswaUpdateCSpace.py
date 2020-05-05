#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import json
import codecs
import time
import datetime
import csv

from dirq.QueueSimple import QueueSimple

from toolbox.cswaHelpers import *
from common import cspace
from common.utils import deURN

from cspace_django_site.main import cspace_django_site

MAINCONFIG = cspace_django_site.getConfig()

DIRQ = QueueSimple('/tmp/cswa')

MAXLOCATIONS = 1000

import xml.etree.ElementTree as etree

def getWhen2Post(config):

    try:
        when2post = config.get('info', 'when2post')
    except:
        # default is update immediately
        when2post = 'update'

    return when2post

def add2queue(requestType, uri, fieldset, updateItems, form):
    userdata = form['userdata']
    element = json.dumps((requestType, uri, userdata.username, userdata.cspace_password, fieldset, updateItems))
    DIRQ.add(element)
    return ''


def updateCspace(fieldset, updateItems, form, config):
    uri = 'collectionobjects' + '/' + updateItems['objectCsid']
    when2post = getWhen2Post(config)
    writeLog(updateItems, uri, 'POST', form, config)

    if when2post == 'update':
        # get the XML for this object
        connection = cspace.connection.create_connection(MAINCONFIG, form['userdata'])
        url = "cspace-services/" + uri
        try:
            url2, content, httpcode, elapsedtime = connection.make_get_request(url)
        except:
            sys.stderr.write("ERROR: problem GETting XML for %s\n" % url)
            raise
        if httpcode != 200:
            sys.stderr.write("ERROR: HTTP response code %s for GET %s\n" % (httpcode, url))
            sys.stderr.write("ERROR: content for %s: \n%s\n" % (url, content))
            return when2post, "ERROR: HTTP response code %s for GET %s\n" % (httpcode, url)
        if content is None:
            sys.stderr.write("ERROR: No XML returned from CSpace server for %s\n" % url)
            return when2post, "ERROR: No XML returned from CSpace server for %s\n" % url
        try:
            message, payload = updateXML(fieldset, updateItems, content)
        except:
            sys.stderr.write("ERROR generating update XML for fieldset %s\n" % fieldset)
            try:
                sys.stderr.write("ERROR: payload for PUT %s: \n%s\n" % (url, payload))
            except:
                sys.stderr.write("ERROR: could not write payload to error log for %s: \n" % url)
            return when2post, "ERROR generating update XML for fieldset %s\n" % fieldset
        try:
            (url3, data, httpcode, elapsedtime) = postxml('PUT', uri, payload, form)
        except:
            sys.stderr.write("ERROR: failed PUT payload for %s: \n%s\n" % (url, payload))
            return when2post, "ERROR: failed PUT payload for %s: \n%s\n" % (url, payload)
        if data is None:
            sys.stderr.write("ERROR: failed PUT payload for %s: \n%s\n" % (url, payload))
            sys.stderr.write("ERROR: HTTP response code %s for  %s\n" % (httpcode, url))
            return when2post, "ERROR: Bad HTTP response code %s for  %s\n" % (httpcode, url)
        # sys.stderr.write("payload for %s: \n%s" % (url, payload))
        # sys.stderr.write("updated object with csid %s to REST API...\n" % updateItems['objectCsid'])
        return when2post, message
    elif when2post == 'queue':
        message = add2queue("PUT", uri, fieldset, updateItems, form)
        return when2post, message
    else:
        return 'invalid move action' % when2post, ''


def createObject(objectinfo, config, form):
    uri = 'collectionobjects'
    when2post = getWhen2Post(config)
    writeLog(objectinfo, uri, 'POST', form, config)

    if when2post == 'update':
        payload = createObjectXML(objectinfo)
        (url, data, csid, elapsedtime) = postxml('POST', uri, payload, form)
        sys.stderr.write("created new object with csid %s to REST API..." % csid)
        return 'created new object', csid
    elif when2post == 'queue':
        add2queue("POST", uri, 'createobject', objectinfo, form)
        return 'queued new object', ''
    else:
        return 'invalid move action' % when2post, ''


def updateLocations(updateItems, config, form):
    uri = 'movements'
    when2post = getWhen2Post(config)
    writeLog(updateItems, uri, 'POST', form, config)

    if when2post == 'update':
        makeMH2R(updateItems, config, form)
        return 'moved', ''
    elif when2post == 'queue':
        add2queue("POST", uri, 'movements', updateItems, form)
        return 'queued move', ''
    else:
        return 'invalid move action' % when2post, ''


def updateXML(fieldset, updateItems, xml):
    message = ''

    # Fields vary with fieldsets
    if fieldset == 'keyinfo':
        fieldList = ('pahmaFieldCollectionPlace', 'assocPeople', 'objectName', 'pahmaEthnographicFileCode')
    elif fieldset == 'namedesc':
        fieldList = ('briefDescription', 'objectName')
    elif fieldset == 'registration':
        # nb:  'pahmaAltNumType' is handled with  'pahmaAltNum'
        fieldList = ('objectName', 'pahmaAltNum', 'fieldCollector')
    elif fieldset == 'hsrinfo':
        fieldList = ('objectName', 'pahmaFieldCollectionPlace', 'briefDescription')
    elif fieldset == 'objtypecm':
        fieldList = ('objectName', 'collection', 'responsibleDepartment', 'pahmaFieldCollectionPlace', 'pahmaTmsLegacyDepartment')
    elif fieldset == 'collection':
        fieldList = ('objectName', 'collection')
    elif fieldset == 'placeanddate':
        fieldList = ('objectName', 'pahmaFieldLocVerbatim', 'pahmaFieldCollectionDate')
    elif fieldset == 'places':
        fieldList = ('pahmaFieldLocVerbatim', 'pahmaFieldCollectionPlace', 'objectProductionPlace', 'contentPlace')
    elif fieldset == 'dates':
        fieldList = ('objectProductionDate', 'pahmaFieldCollectionDate', 'contentDate', 'briefDescription')
    elif fieldset == 'mattax':
        fieldList = ('material', 'taxon', 'briefDescription')
    elif fieldset == 'student':
        fieldList = ('taxon', 'fieldLocCountry', 'fieldLocState', 'fieldLocCounty')
    elif fieldset == 'fullmonty':
        fieldList = ('assocPeople', 'briefDescription', 'collection', 'contentDate', 'contentPlace', 'fieldCollector', 'material',
        'objectName', 'objectName', 'objectProductionDate', 'objectProductionPlace', 'objectProductionPerson', 'pahmaAltNum', 'pahmaEthnographicFileCode',
        'pahmaFieldCollectionDate', 'pahmaFieldCollectionPlace', 'pahmaFieldLocVerbatim', 'pahmaObjectStatus', 'responsibleDepartment',
        'taxon', 'material')

    root = etree.fromstring(xml)
    # add the user's changes to the XML
    for relationType in fieldList:
        # sys.stderr.write('tag1: %s\n' % relationType)
        # this app does not insert empty values into anything!
        if not relationType in updateItems.keys() or updateItems[relationType] == '':
            continue
        listSuffix = 'List'
        extra = ''
        if relationType in ['assocPeople', 'pahmaAltNum', 'pahmaFieldCollectionDate', 'objectProductionDate', 'objectProductionPlace', 'objectProductionPerson', 'contentDate', 'material', 'taxon', 'fieldLocCountry', 'fieldLocState', 'fieldLocCounty']:
            extra = 'Group'
        elif relationType in ['briefDescription', 'fieldCollector', 'responsibleDepartment', 'contentPlace']:
            listSuffix = 's'
        if relationType in ['collection', 'pahmaFieldLocVerbatim', 'contentDate', 'pahmaTmsLegacyDepartment']:
            listSuffix = ''
        else:
            pass
            # html += ">>> ",'.//'+relationType+extra+'List'
        # sys.stderr.write('tag2: %s\n' % (relationType + extra + listSuffix))
        if relationType == 'taxon':
            tmprelationType = 'taxonomicIdent'
        elif relationType in ['fieldLocCountry', 'fieldLocState', 'fieldLocCounty']:
            tmprelationType = 'locality'
        else:
            tmprelationType = relationType
        metadata = root.findall('.//' + tmprelationType + extra + listSuffix)
        if 'objectNumber' in updateItems and updateItems['objectNumber'] == '':
            updateItems['objectNumber'] = root.find('.//objectNumber').text
        try:
            metadata = metadata[0]  # there had better be only one!
        except:
            # hmmm ... we didn't find this element in the record. Make a note a carry on!
            # message += 'No "' + relationType + extra + listSuffix + '" element found to update.'
            continue
        # html += ">>> ",relationType,':',updateItems[relationType]
        if relationType in ['assocPeople', 'objectName', 'pahmaAltNum', 'material', 'taxon', 'objectProductionPerson', 'objectProductionPlace', 'fieldLocCountry', 'fieldLocState', 'fieldLocCounty']:
            # group = metadata.findall('.//'+relationType+'Group')
            # sys.stderr.write('  updateItem: ' + relationType + ':: ' + updateItems[relationType] + '\n' )
            Entries = metadata.findall('.//' + relationType)
            # if this value does not already exist, we shall add it as a new first element
            if not alreadyExists(updateItems[relationType], Entries):
                newElement = etree.Element(tmprelationType + 'Group')
                # these 3 fields can only appear once per group, so reuse (replace) them if they appear
                if relationType in ['fieldLocCountry', 'fieldLocState', 'fieldLocCounty']:
                    try:
                        newElement = metadata.findall('.//' + tmprelationType + 'Group')[0]
                    except:
                        pass
                leafElement = etree.Element(relationType)
                leafElement.text = updateItems[relationType]
                newElement.append(leafElement)
                if relationType == 'objectName':
                    for m in 'objectNameType objectNameSystem objectNameCurrency objectNameNote objectNameNote objectNameLevel objectNameLanguage'.split(' '):
                        leafElement = etree.Element(m)
                        newElement.append(leafElement)
                if relationType == 'material':
                    for m in 'materialName materialComponent materialComponentNote materialSource'.split(' '):
                        leafElement = etree.Element(m)
                        newElement.append(leafElement)
                if relationType == 'taxon':
                    for m in 'refPage notes taxonomicIdentHybridParentGroupList affinityTaxon reference institution identBy identDateGroup identKind taxonomicIdentHybridName qualifier hybridFlag'.split(' '):
                        leafElement = etree.Element(m)
                        if m == 'identDateGroup':
                            date_element = etree.Element('dateDisplayDate')
                            leafElement.append(date_element)
                        newElement.append(leafElement)
                for r in 'objectProductionPerson objectProductionPlace'.split(' '):
                    if r == relationType:
                        leafElement = etree.Element(r + 'Role')
                        newElement.append(leafElement)
                if relationType in ['assocPeople', 'pahmaAltNum']:
                    apgType = etree.Element(relationType + 'Type')
                    # this needs to be a refname for PAHMA's assocpeopletype...
                    apgType.text = updateItems[relationType + 'Type'] if relationType == 'pahmaAltNum' else "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(assocpeople):item:name(assocpeopletype06)'made by'"
                    # sys.stderr.write(relationType + 'Type:' + updateItems[relationType + 'Type'])
                    newElement.append(apgType)
                    leafElement = etree.Element(relationType + 'Note')
                    newElement.append(leafElement)
                if (len(Entries) == 1 and Entries[0].text is None) or tmprelationType == 'locality':
                    # sys.stderr.write('reusing empty element: %s\n' % Entries[0].tag)
                    # sys.stderr.write('ents : %s\n' % Entries[0].text)
                    for child in metadata:
                        # html += '<br>tag: ', child.tag
                        if child.tag == tmprelationType + 'Group':
                            # html += '<br> found it! ',child.tag
                            metadata.remove(child)
                    metadata.insert(0, newElement)
                else:
                    metadata.insert(0, newElement)
            else:
                if IsAlreadyPreferred(updateItems[relationType], Entries):
                    continue
                else:
                    # exists, but not preferred. make it the preferred: remove it from where it is, insert it as 1st
                    for child in metadata:
                        if child.tag == tmprelationType + 'Group':
                            checkval = child.find('.//' + relationType)
                            if checkval.text == updateItems[relationType]:
                                savechild = child
                                metadata.remove(child)
                    metadata.insert(0, savechild)
                pass
        elif relationType in ['briefDescription', 'fieldCollector', 'responsibleDepartment', 'contentPlace']:
            Entries = metadata.findall('.//' + relationType)
            # for e in Entries:
            # html += '%s, %s<br>' % (e.tag, e.text)
            # sys.stderr.write(' e: %s\n' % e.text)
            if alreadyExists(updateItems[relationType], Entries):
                if IsAlreadyPreferred(updateItems[relationType], Entries):
                    # message += "%s exists as %s, already preferred;" % (updateItems[relationType],relationType)
                    pass
                else:
                    # exists, but not preferred. make it the preferred: remove it from where it is, insert it as 1st
                    for child in Entries:
                        sys.stderr.write(' c: %s\n' % child.tag)
                        if child.text == updateItems[relationType]:
                            new_element = child
                            metadata.remove(child)
                            # message += '%s removed. len = %s<br/>' % (child.text, len(Entries))
                    metadata.insert(0, new_element)
                    message += "'%s' exists in %s, now preferred.<br/>" % (deURN(updateItems[relationType]), relationType)
                    # html += 'already exists: %s<br>' % updateItems[relationType]
            # check if the existing element is empty; if so, use it, don't add a new element
            else:
                if len(Entries) == 1 and Entries[0].text is None:
                    # message += "removed %s ;<br/>" % (Entries[0].tag)
                    metadata.remove(Entries[0])
                new_element = etree.Element(relationType)
                new_element.text = updateItems[relationType]
                metadata.insert(0, new_element)
                message += "added '%s' as the preferred term in %s.<br/>" % (deURN(updateItems[relationType]), relationType)

        elif relationType in ['objectProductionDate', 'pahmaFieldCollectionDate', 'contentDate']:
            # we'll be replacing the entire structured date group
            newDateGroup = etree.Element('%sGroup' % relationType)
            new_element = etree.Element('dateDisplayDate')
            new_element.text = updateItems[relationType]
            newDateGroup.insert(0, new_element)

            DateGroup = metadata.find('.//%sGroup' % relationType)
            if DateGroup is not None:
                metadata.remove(DateGroup)
            # one of many special cases...
            if relationType == 'contentDate':
                DateGroup = metadata.findall('.//*')
                [metadata.remove(d) for d in DateGroup]
                metadata.insert(0, new_element)
            else:
                metadata.insert(0, newDateGroup)
        else:
            # check if value is already present. if so, skip
            if alreadyExists(updateItems[relationType], metadata.findall('.//' + relationType)):
                if IsAlreadyPreferred(updateItems[relationType], metadata.findall('.//' + relationType)):
                    continue
                else:
                    message += "'%s' already exists as an NPT in %s: This value has been inserted as the PT and in doing so is now duplicated.<br/>" % (
                        deURN(updateItems[relationType]), relationType)
                    pass
            newElement = etree.Element(relationType)
            newElement.text = updateItems[relationType]
            metadata.insert(0, newElement)
    objectCount = root.find('.//numberOfObjects')
    if 'objectCount' in updateItems:
        if objectCount is None:
            objectCount = etree.Element('numberOfObjects')
            collectionobjects_common = root.find(
                './/{http://collectionspace.org/services/collectionobject}collectionobjects_common')
            collectionobjects_common.insert(0, objectCount)
        objectCount.text = updateItems['objectCount']

    inventoryCount = root.find('.//inventoryCount')
    if 'inventoryCount' in updateItems:
        if inventoryCount is None:
            inventoryCount = etree.Element('inventoryCount')
            collectionobjects_pahma = root.find(
                './/{http://collectionspace.org/services/collectionobject/local/pahma}collectionobjects_pahma')
            collectionobjects_pahma.insert(0, inventoryCount)
        inventoryCount.text = updateItems['inventoryCount']
    for fld in 'pahmaTmsLegacyDepartment pahmaFieldLocVerbatim'.split(' '):
        if fld in updateItems and updateItems[fld] != '':
            fldtoupdate = root.find('.//' + fld)
            if fldtoupdate is None:
                fldtoupdate = etree.Element(fld)
                collectionobjects_pahma = root.find('.//{http://collectionspace.org/services/collectionobject/local/pahma}collectionobjects_pahma')
                collectionobjects_pahma.insert(0, fldtoupdate)
            fldtoupdate.text = updateItems[fld]

    collection = root.find('.//collection')
    if 'collection' in updateItems:
        if collection is None:
            collection = etree.Element('collection')
            collectionobjects_common = root.find(
                './/{http://collectionspace.org/services/collectionobject}collectionobjects_common')
            collectionobjects_common.insert(0, collection)
            message += " %s added as &lt;%s&gt;.<br/>" % (deURN(updateItems['collection']), 'collection')
        collection.text = updateItems['collection']

    payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(root, encoding='unicode')
    # update collectionobject..
    # html += "<br>pretending to post update to %s to REST API..." % updateItems['objectCsid']
    # elapsedtimetotal = time.time()
    # messages = []
    # messages.append("posting to %s REST API..." % uri)
    # print(payload)
    # messages.append(payload)

    return message, payload


def createObjectXML(objectinfo):

    # get the XML for this object
    content = '''<document name="collectionobjects">
<ns2:collectionobjects_common xmlns:ns2="http://collectionspace.org/services/collectionobject" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<objectNameList>
<objectNameGroup>
<objectName/>
</objectNameGroup>
</objectNameList>
<objectNumber/>
</ns2:collectionobjects_common>
</document>'''

    x = '''
<ns2:collectionobjects_omca xmlns:ns2="http://collectionspace.org/services/collectionobject/local/omca" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<sortableObjectNumber/>
</ns2:collectionobjects_omca>
'''

    root = etree.fromstring(content)
    for elementname in objectinfo:
        if elementname in objectinfo:
            element = root.find('.//' + elementname)
            element.text = objectinfo[elementname]

    uri = 'collectionobjects'
    payload = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(root, encoding='utf-8')
    # update collectionobject..
    # sys.stderr.write("post new object %s to REST API..." % objectinfo['objectNumber'])

    return '', payload


def makeMH2R(updateItems, config, form):
    institution = config.get('info', 'institution')

    try:
        uri = 'movements'

        # html += "<br>posting to movements REST API..."
        payload = lmiPayload(updateItems, institution)
        (url, data, movementcsid, elapsedtime) = postxml('POST', uri, payload, form)
        updateItems['subjectCsid'] = movementcsid

        uri = 'relations'

        # html += "<br>posting inv2obj to relations REST API..."
        updateItems['subjectDocumentType'] = 'Movement'
        updateItems['objectDocumentType'] = 'CollectionObject'
        payload = relationsPayload(updateItems)
        (url, data, ignorecsid, elapsedtime) = postxml('POST', uri, payload, form)

        # reverse the roles
        # html += "<br>posting obj2inv to relations REST API..."
        temp = updateItems['objectCsid']
        updateItems['objectCsid'] = updateItems['subjectCsid']
        updateItems['subjectCsid'] = temp
        updateItems['subjectDocumentType'] = 'CollectionObject'
        updateItems['objectDocumentType'] = 'Movement'
        payload = relationsPayload(updateItems)
        (url, data, ignorecsid, elapsedtime) = postxml('POST', uri, payload, form)

        writeLog(updateItems, uri, 'POST', form, config)

        # html += "<h3>Done w update!</h3>"
    except Exception as e:
        print(e[0])
        raise


def postxml(requestType, uri, payload, form):
    connection = cspace.connection.create_connection(MAINCONFIG, form['userdata'])
    return connection.postxml(uri="cspace-services/" + uri, payload=payload, requesttype=requestType)


def writeLog(updateItems, uri, httpAction, form, config):
    auditFile = config.get('files', 'auditfile')
    # TODO: unsnarl this someday. there should be only one way to specify which tool is in use.
    # TODO: and only one place all the logging should go (I think: not sure about audit trail...)
    try:
        updateType = form['tool']
    except:
        updateType = updateItems['updateType']
    try:
        username = form['userdata']
        username = username.username
    except:
        username = ''
    try:
        csvlogfh = csv.writer(codecs.open(auditFile, 'a', 'utf-8'), delimiter="\t")
        logrec = [httpAction, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), updateType, uri, username]
        for item in updateItems.keys():
            logrec.append("%s=%s" % (item, updateItems[item].replace('\n', '#')))
        csvlogfh.writerow(logrec)
    except:
        raise
        # html += 'writing to log %s failed!' % auditFile
        pass

