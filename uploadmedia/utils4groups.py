from cswaExtras import postxml, relationsPayload


def add2group(groupcsid, list_of_objects, http_parms):

    uri = 'relations'

    if len(list_of_objects) == 0:
        return ['no objects added to the group.']

    messages = []
    seen = {}
    duplicates = {}

    for object in list_of_objects:
        # messages.append("posting group2obj to relations REST API...")

        if object in seen:
            # it's a duplicate, skip it
            duplicates[object] = True
            messages.append('duplicate item %s not added again' % object)
            continue
        else:
            seen[object] = True

        # "urn:cspace:institution.cspace.berkeley.edu:group:id(%s)" % groupCSID
        groupElements = {}
        groupElements['objectDocumentType'] = 'CollectionObject'
        groupElements['subjectDocumentType'] = 'Group'
        groupElements['objectCsid'] = object
        groupElements['subjectCsid'] = groupcsid

        payload = relationsPayload(groupElements)
        (url, data, csid, elapsedtime) = postxml('POST', uri, http_parms.realm, http_parms.server,
                                                 http_parms.username, http_parms.password, payload)
        # elapsedtimetotal += elapsedtime
        # messages.append('got relation csid %s elapsedtime %s ' % (csid, elapsedtime))
        groupElements['group2objCSID'] = csid
        # messages.append("relations REST API post succeeded...")

        # reverse the roles
        # messages.append("posting obj2group to relations REST API...")
        temp = groupElements['objectCsid']
        groupElements['objectCsid'] = groupElements['subjectCsid']
        groupElements['subjectCsid'] = temp
        groupElements['objectDocumentType'] = 'Group'
        groupElements['subjectDocumentType'] = 'CollectionObject'
        payload = relationsPayload(groupElements)
        (url, data, csid, elapsedtime) = postxml('POST', uri, http_parms.realm, http_parms.server,
                                                 http_parms.username, http_parms.password, payload)

        # elapsedtimetotal += elapsedtime
        # messages.append('got relation csid %s elapsedtime %s ' % (csid, elapsedtime))
        groupElements['obj2groupCSID'] = csid
        # messages.append("relations REST API post succeeded...")

    messages.append('%s item(s) added to group' % len(list_of_objects))
    return messages


def create_group(grouptitle, http_parms):
    payload = """
        <document name="groups">
            <ns2:groups_common xmlns:ns2="http://collectionspace.org/services/group" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <title>%s</title>
            </ns2:groups_common>
        </document>
        """ % grouptitle

    (url, data, csid, elapsedtime) = postxml('POST', 'groups', http_parms.realm, http_parms.server, http_parms.username,
                                                  http_parms.password, payload)
    return csid

