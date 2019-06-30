import urllib
import time
import re
import json
import configparser

from toolbox.cswaUpdateCSpace import updateXML, createObjectXML, writeLog
from toolbox.cswaHelpers import *

QUEUECONFIG = configparser.RawConfigParser()
QUEUECONFIG.read('queue.cfg')


def processqueueelement(element):

    realm = QUEUECONFIG.get('connect', 'realm')
    hostname = QUEUECONFIG.get('connect', 'hostname')
    institution = QUEUECONFIG.get('info', 'institution')

    requestType, uri, username, password, fieldset, updateItems = json.loads(element)

    if uri == 'collectionobjects' and requestType == 'POST':
        payload = createObjectXML(updateItems)
        (url, data, csid, elapsedtime) = postxml(requestType, uri, realm, hostname, username, password, payload)
    if 'collectionobjects' == uri and requestType == 'PUT':

        uri = 'collectionobjects'
        getItems = updateItems['objectCsid']

        # get the XML for this object
        url, content, elapsedtime = getxml(uri, realm, hostname, username, password, getItems)
        message, payload = updateXML(fieldset, updateItems, content)
        (url, data, csid, elapsedtime) = postxml(requestType, uri, realm, hostname, username, password, payload)

    elif 'movements' in uri:

        uri = 'movements'

        # html += "<br>posting to movements REST API..."
        payload = lmiPayload(updateItems, institution)
        (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
        updateItems['subjectCsid'] = csid

        uri = 'relations'

        # html += "<br>posting inv2obj to relations REST API..."
        updateItems['subjectDocumentType'] = 'Movement'
        updateItems['objectDocumentType'] = 'CollectionObject'
        payload = relationsPayload(updateItems)
        (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)

        # reverse the roles
        # html += "<br>posting obj2inv to relations REST API..."
        temp = updateItems['objectCsid']
        updateItems['objectCsid'] = updateItems['subjectCsid']
        updateItems['subjectCsid'] = temp
        updateItems['subjectDocumentType'] = 'CollectionObject'
        updateItems['objectDocumentType'] = 'Movement'
        payload = relationsPayload(updateItems)
        (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)

        uri = 'movements'

    writeLog(updateItems, uri, requestType, '', QUEUECONFIG)



def getxml(uri, realm, hostname, username, password, getItems):
    # port and protocol need to find their ways into the config files...
    port = ''
    protocol = 'https'
    server = protocol + "://" + hostname + port
    passman = urllib.request.HTTPPasswordMgr()
    passman.add_password(realm, server, username, password)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
    if getItems == None:
        url = "%s/cspace-services/%s" % (server, uri)
    else:
        url = "%s/cspace-services/%s/%s" % (server, uri, getItems)
    #sys.stderr.write('url %s' % url )
    elapsedtime = 0.0

    try:
        elapsedtime = time.time()
        f = urllib.request.urlopen(url)
        data = f.read()
        elapsedtime = time.time() - elapsedtime
    except urllib.error.HTTPError as e:
        sys.stderr.write('The server couldn\'t fulfill the request.')
        sys.stderr.write( 'Error code: %s' % e.code)
        raise
    except urllib.error.URLError as e:
        sys.stderr.write('We failed to reach a server.')
        sys.stderr.write( 'Reason: %s' % e.reason)
        raise
    else:
        return (url, data, elapsedtime)


def postxml(requestType, uri, realm, hostname, username, password, payload):
    port = ''
    protocol = 'https'
    server = protocol + "://" + hostname + port
    passman = urllib.request.HTTPPasswordMgr()
    passman.add_password(realm, server, username, password)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
    url = "%s/cspace-services/%s" % (server, uri)
    elapsedtime = 0.0

    elapsedtime = time.time()
    request = urllib.request.Request(url, payload, {'Content-Type': 'application/xml'})
    # default method for urllib2 with payload is POST
    if requestType == 'PUT': request.get_method = lambda: 'PUT'
    try:
        f = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            sys.stderr.write('We failed to reach a server.\n')
            sys.stderr.write('Reason: ' + str(e.reason) + '\n')
        if hasattr(e, 'code'):
            sys.stderr.write('The server couldn\'t fulfill the request.\n')
            sys.stderr.write('Error code: ' + str(e.code) + '\n')
        if True:
            #print('Error in POSTing!')
            sys.stderr.write("Error in POSTing!\n")
            sys.stderr.write(url)
            sys.stderr.write(payload)
            raise

    data = f.read()
    info = f.info()
    # if a POST, the Location element contains the new CSID
    if info.getheader('Location'):
        csid = re.search(uri + '/(.*)', info.getheader('Location'))
        csid = csid.group(1)
    else:
        csid = ''
    elapsedtime = time.time() - elapsedtime
    return (url, data, csid, elapsedtime)