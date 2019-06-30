"""

"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from .views import index

import time, sys
from common import cspace
from os import path
#from cspace_django_site import settings


from cspace_django_site.main import cspace_django_site

# alas, there are many ways the XML parsing functionality might be installed.
# the following code attempts to find and import the best...
try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring

    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree

        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree

            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree

                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jblowe@berkeley.edu', email='xxx', password='pumpkins99')

    def test_grouper(self):
        # Create an instance of a GET request.
        request = self.factory.get('/csvimport')

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        #request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def getfromCSpace(uri, request):
        connection = cspace.connection.create_connection(cspace_django_site, request.user)
        url = "cspace-services/" + uri
        return connection.make_get_request(url)

    def find_group(request, grouptitle, pgSz):

        # TIMESTAMP = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

        asquery = '%s?as=%s_common%%3Atitle%%3D%%27%s%%27&wf_deleted=false&pgSz=%s' % (
        'groups', 'groups', grouptitle, pgSz)

        # Make authenticated connection to cspace server...
        (groupurl, grouprecord, dummy, elapsedtime) = getfromCSpace(asquery, request)
        if grouprecord is None:
            return (None, None, 0, [], 'Error: the search for group \'%s.\' failed.' % grouptitle)
        grouprecordtree = fromstring(grouprecord)
        groupcsid = grouprecordtree.find('.//csid')
        if groupcsid is None:
            return (None, None, 0, [], None)
        groupcsid = groupcsid.text

        uri = 'collectionobjects?rtObj=%s&pgSz=%s' % (groupcsid, pgSz)
        try:
            (groupurl, groupmembers, dummy, elapsedtime) = getfromCSpace(uri, request)
            groupmembers = fromstring(groupmembers)
            totalItems = groupmembers.find('.//totalItems')
            totalItems = int(totalItems.text)
            objectcsids = [e.text for e in groupmembers.findall('.//csid')]
        except:
            return (None, None, 0, [], 'Error: we could not make list of group members')

        return grouptitle, groupcsid, totalItems, objectcsids, None


    def find_group_relations(request, groupcsid):

        TIMESTAMP = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

        relationcsids = []
        for qtype in 'obj sbj'.split(' '):
            relationsquery = 'relations?%s=%s&pgSz=1000' % (qtype, groupcsid)

            # Make authenticated connection to ucjeps.cspace...
            (groupurl, searchresult, dummy, elapsedtime) = getfromCSpace(relationsquery, request)
            if searchresult is None:
                return (None, None, 'Error: We could not find the groupcsid \'%s.\' Please try another.' % groupcsid)
            relationlist = fromstring(searchresult)

            relations = relationlist.findall('.//relation-list-item')
            if relations is not None:
                for r in relations:
                    relationcsids.append([e.text for e in r.findall('.//csid')])

        return relationcsids

