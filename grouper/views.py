__author__ = 'jblowe'

import os
import re
import time
import urllib

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common.utils import setConstants
from common.appconfig import loadConfiguration, loadFields, getParms
from common import cspace # we use the config file reading function
from grouputils import find_group, create_group, add2group, delete_from_group, setup_solr_search
from cspace_django_site import settings
from os import path
from .models import AdditionalInfo

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'grouper')

# read common config file
common = 'common'
prmz = loadConfiguration(common)
print 'Configuration for %s successfully read' % common

groupConfig = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'grouper')
prmz.FIELDDEFINITIONS = groupConfig.get('grouper', 'FIELDDEFINITIONS')

# add in the the field definitions...
prmz = loadFields(prmz.FIELDDEFINITIONS, prmz)

# override / add a couple parameters for this app
prmz.MAXRESULTS = int(groupConfig.get('grouper', 'MAXRESULTS'))
prmz.TITLE = groupConfig.get('grouper', 'TITLE')
prmz.NUMBERFIELD = groupConfig.get('grouper', 'NUMBERFIELD')
prmz.CSIDFIELD = groupConfig.get('grouper', 'CSIDFIELD')

print 'Configuration for %s successfully read' % 'grouper'

def remove_items(context):
    for item in 'groupaction items labels count'.split(' '):
        try:
            del context[item]
        except:
            pass

@login_required()
def index(request):

    context = setConstants({}, prmz, request)
    context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)

    if request.method == 'POST':
        prmz.MAXFACETS = 0
        context['searchValues'] = {'map-bmapper': '', 'querystring': ''}
        context['maxresults'] = prmz.MAXRESULTS
        context['displayType'] = 'list'

        context['objects'] = request.POST['objects']
        context['group'] = request.POST['gr.group']

        messages = []
        groupcsid = None
        queryterms = []

        if 'submit' in request.POST:
            # we piggyback on the "bmapper search handling" here: we don't want
            # doSearch to construct the query string for us 'cause it won't
            # do it right: we make our own below that merges the group results (if any)
            # with the list of object numbers (if any)
            if 'gr.group' in request.POST:
                group = request.POST['gr.group']
                if group == '':
                    messages = ['A value for group title (either an existing group or a potential new one) is required.']
                else:
                    grouptitle, groupcsid, totalItems, list_of_objects, errormsg = find_group(request, urllib.quote_plus(group), prmz.MAXRESULTS)

                    if groupcsid is not None:
                        if len(list_of_objects) > 0:
                            queryterms.append(prmz.CSIDFIELD + ':(' + " OR ".join(list_of_objects) + ')')
                        context['groupaction'] = 'Update Group'
                    else:
                        context['groupaction'] = 'Create Group'

                    if totalItems > prmz.MAXRESULTS:
                        messages += ['This group has %s members and so is too big for Grouper. Maximum number of members Grouper can handle is %s' % (totalItems, prmz.MAXRESULTS)]
                        remove_items(context)
                    if errormsg is not None:
                        messages.append(errormsg)
                        remove_items(context)

            if 'objects' in request.POST:
                objectnumbers = request.POST['objects'].strip()
                objectnumbers = re.sub(r"[\r\n ]+", ' ', objectnumbers)
                if objectnumbers == '':
                    pass
                else:
                    objectnumbers_escaped = objectnumbers.replace(')','\)').replace('(','\(').replace('+','\+')
                    objectnumbers_escaped = objectnumbers_escaped.split(' ')
                    objectnumbers = objectnumbers.split(' ')
                    if len(objectnumbers) > 0:
                        queryterms.append('%s: (' % prmz.NUMBERFIELD + " OR ".join(objectnumbers_escaped) + ')')

            if 'groupaction' in context:
                context = setup_solr_search(queryterms, context, prmz, request)
                if 'count' in context and context['count'] > prmz.MAXRESULTS:
                    messages += ['This group is too big for Grouper. Maximum number of members is %s' % prmz.MAXRESULTS]
                    remove_items(context)
                elif 'items' in context:
                    object_numbers_found = [item['accession'] for item in context['items']]
                    obj2csid = [[item['csid'], item['accession']] for item in context['items'] if item['accession'] in objectnumbers]
                    # if we are dealing with a group that already exists, we need to avoid inserting duplicates
                    messages += ['"%s" not found and so not included.' % accession for accession in objectnumbers if accession not in object_numbers_found ]
                    if groupcsid is not None:
                        messages += ['"%s" already in member list and so not duplicated.' % item[1] for item in obj2csid if item[0] in list_of_objects]
                    if prmz.MAXRESULTS < context['count']:
                        messages += ['Only %s items of %s are displayed below and can be managed.' % (prmz.MAXRESULTS, context['count'])]
                else:
                    messages += ['problem with Solr query: %s' % context['searchValues']['querystring'] ]

        elif 'updategroup' in request.POST:
            group = request.POST['gr.group']
            # it's complicated: we can't search in Solr for the group, as we may have just created or updated it.
            # so we have to do REST calls to find the group and its CSIDs, then we can search Solr
            # though we might still miss some... :-(
            grouptitle, groupcsid, totalItems, list_of_objects, errormsg = find_group(request, urllib.quote_plus(group), prmz.MAXRESULTS)
            if groupcsid is None:
                groupcsid = create_group(group, request)
                context['items'] = []
            else:
                if len(list_of_objects) > 0:
                    queryterms = ['%s: (' % prmz.CSIDFIELD + " OR ".join(list_of_objects) + ')']
                context = setup_solr_search(queryterms, context, prmz, request)
                if prmz.MAXRESULTS < len(context['items']):
                    messages += ['Only %s items of %s are displayed below.' % (prmz.MAXRESULTS, context['items'])]
            items2add = []
            items2delete = []
            items_ignored = []
            items_included = []
            for item in request.POST:
                if "item-" in item:
                    items_included.append(request.POST[item])
                    # add this item to the group if it's not a member already
                    if request.POST[item] in list_of_objects:
                        pass
                    else:
                        items2add.append(request.POST[item])
            object_numbers_found = [item['csid'] for item in context['items']]
            for i, item in enumerate(object_numbers_found):
                if item in items_included:
                    pass
                else:
                    items2delete.append(item)

            messages += add2group(groupcsid, items2add, request)
            messages += delete_from_group(groupcsid, items2delete, request)
            grouptitle, groupcsid, totalItems, list_of_objects, errormsg = find_group(request, urllib.quote_plus(group), prmz.MAXRESULTS)
            if len(items_ignored) > 0 : messages += ['%s items in group untouched.' % len(items_ignored)]
            queryterms = [ '%s: (' % prmz.CSIDFIELD + " OR ".join(list_of_objects) + ')' ]
            context = setup_solr_search(queryterms, context, prmz, request)

        if len(messages) > 0:
            context['messages'] = messages
        return render(request, 'grouper.html', context)

    else:
        
        return render(request, 'grouper.html', context)
