#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import copy
import csv
import time
import datetime
import cgi
import re

from django.http import HttpResponse
from collections import Counter

MAXLOCATIONS = 1000

import toolbox.cswaDB as cswaDB
import toolbox.cswaConstants as cswaConstants
import toolbox.cswaGetAuthorityTree as cswaGetAuthorityTree
import toolbox.cswaConceptutils as concept
import toolbox.cswaSMBclient as cswaSMBclient
from toolbox.cswaHelpers import *
# these are the three functions that do updates
from toolbox.cswaUpdateCSpace import updateCspace, createObject, updateLocations
from toolbox.cswaRows import formatRow, setRefnames
from cspace_django_site.main import cspace_django_site

MAINCONFIG = cspace_django_site.getConfig()


def serverCheck(form, config):
    result = '<tr><td class="zcell">start server check</td><td class="zcell">' + time.strftime("%b %d %Y %H:%M:%S", time.localtime()) + "</td></tr>"

    elapsedtime = time.time()
    # do an sql search...
    result += '<tr><td class="zcell">SQL check</td><td class="zcell">' + cswaDB.testDB(config) + "</td></tr>"
    elapsedtime = time.time() - elapsedtime
    result += '<tr><td class="zcell">SQL time</td><td class="zcell">' + ('%8.2f' % elapsedtime) + " seconds</td></tr>"

    # if we are configured for barcodes, try that...
    try:
        config.get('files', 'cmdrfileprefix') + config.get('files', 'cmdrauditfile')
        try:
            elapsedtime = time.time()
            result += '<tr><td class="zcell">barcode audit file</td><td class="zcell">' + config.get('files', 'cmdrauditfile') + "</td></tr>"
            result += '<tr><td class="zcell">trying...</td><td class="zcell"> to write empty test files to commanderWatch directory</td></tr>'
            printers, selected, printerlist = cswaConstants.getPrinters(form)
            for printer in printerlist:
                result += ('<tr><td class="zcell">location labels @ %s</td><td class="zcell">' % printer[1]) + writeCommanderFile('test', printer[1], 'locationLabels', 'locations',  [], config) + "</td></tr>"
                result += ('<tr><td class="zcell">object labels @ %s</td><td class="zcell">' % printer[1]) + writeCommanderFile('test', printer[1], 'objectLabels', 'objects', [], config) + "</td></tr>"
            elapsedtime = time.time() - elapsedtime
            result += '<tr><td class="zcell">barcode check time</td><td class="zcell">' + ('%8.2f' % elapsedtime) + " seconds</td></tr>"
        except:
            result += '<tr><td class="zcell">barcode functionality check</td><td class="zcell"><span class="error">FAILED.</span></td></tr>'
    except:
        result += '<tr><td class="zcell">barcode functionality check</td><td class="zcell">skipped, not configured in config file.</td></tr>'

    elapsedtime = time.time()
    # rest check...
    elapsedtime = time.time() - elapsedtime
    result += '<tr><td class="zcell">REST check</td><td class="zcell">Not ready yet.</td></tr>'
    #result += "<tr><td class="zcell">REST check</td><td class="zcell">" + ('%8.2f' % elapsedtime) + " seconds</td></tr>"

    result += '<tr><td class="zcell">end server check</td><td class="zcell">' + time.strftime("%b %d %Y %H:%M:%S", time.localtime()) + "</td></tr>"
    result += '''<tr><td colspan="2"></td></tr>'''

    return '''<table><tbody><tr><td><h3>Server Status Check</h3></td></tr>''' + result + '''</tbody></table>'''


def makeGroup(form,config):
    pass


def listAuthorities(authority, primarytype, authItem, config, form, displaytype):
    if authItem == None or authItem == '': return False, '', []
    rows = cswaGetAuthorityTree.getAuthority(authority, primarytype, authItem, config.get('connect', 'connect_string'))

    hasDups, html = listSearchResults(authority, config, displaytype, form, rows)

    return hasDups, html, rows
    #return rows


def doComplexSearch(form, config, displaytype):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    hasDups, x, r = listAuthorities('taxon', 'TaxonTenant35', form.get("ut.taxon"), config, form, displaytype)
    html += x
    hasDups, x, r = listAuthorities('locations', 'Locationitem', form.get("lo.location1"), config, form, displaytype)
    html += x
    hasDups, x, r = listAuthorities('places', 'Placeitem', form.get("px.place"), config, form, displaytype)
    html += x
    #listAuthorities('taxon',     'TaxonTenant35',  form.get("ob.objectnumber"),config, form, displaytype)
    #listAuthorities('concepts',  'TaxonTenant35',  form.get("cx.concept"),     config, form, displaytype)

    html += getTableFooter(config, displaytype, updateType, '')
    return html


def doLocationSearch(form, config, displaytype):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    if form.get('lo.location1') == '':
        return '<h3 class="error">Please enter at least a starting location!</h3>'

    try:
        #If barcode print, assume empty end location is start location
        if updateType == "barcodeprint":
            rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), 500, config)
        else:
            rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), MAXLOCATIONS, config)
    except:
        raise

    hasDups, html = listSearchResults('locations', config, displaytype, form, rows)

    if hasDups:
        html += getTableFooter(config, 'error', updateType, 'Please eliminate duplicates and try again!')
        return
    if len(rows) != 0: html += getTableFooter(config, displaytype, updateType, '')
    return html


def doObjectSearch(form, config, displaytype):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    if form.get('ob.objno1') == '':
        return '<h3 class="error">Please enter at least a starting object number!</h3>'

    if updateType == 'moveobject':
        crate = verifyLocation(form.get("lo.crate"), form, config)
        toLocation = verifyLocation(form.get("lo.location1"), form, config)

        if str(form.get("lo.crate")) != '' and crate == '':
            html += '<span class="error">Crate is not valid! Sorry!</span><br/>'
        if toLocation == '':
            html += '<span class="error">Destination is not valid! Sorry!</span><br/>'
        if (str(form.get("lo.crate")) != '' and crate == '') or toLocation == '':
            return html

        toRefname = cswaDB.getrefname('locations_common', toLocation, config)
        toCrate = cswaDB.getrefname('locations_common', crate, config)


    rows, msg = cswaDB.getobjlist('range', form.get("ob.objno1"), form.get("ob.objno2"), 500, config)

    if len(rows) == 0:
        return '<h3 class="error">No objects in this range! Sorry!</h3>'
    else:
        totalobjects = 0
        if updateType == 'objinfo':
            html += cswaConstants.infoHeaders(form.get('fieldset'))
        else:
            html += cswaConstants.getHeader(updateType,institution)
        for r in rows:
            totalobjects += 1
            html += formatRow({'rowtype': updateType, 'data': r}, form, config)

        html += '\n</table><table width="100%"'
        html += """<tr><td align="center" colspan="3">"""
        msg = "Caution: clicking on the button at left will update <b>ALL %s objects</b> shown on this page!" % totalobjects
        html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="3">%s</td></tr>''' % msg
        html += "\n</table>"

        if updateType == 'moveobject':
            html += '<input type="hidden" name="toRefname" value="%s">' % toRefname
            html += '<input type="hidden" name="toCrate" value="%s">' % toCrate
            html += '<input type="hidden" name="toLocAndCrate" value="%s: %s">' % (toLocation, crate)

    return html

def doOjectRangeSearch(form, config, displaytype=''):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)

    valid, error = validateParameters(form, config)
    if not valid: return html + error

    objs, msg = cswaDB.getobjlist('range', form.get("ob.objno1"), form.get("ob.objno2"), 1000, config)

    if len(objs) == 0:
        return '<h3 class="error">No objects in this range! Sorry!</h3>'

    html += """
    <table><tr>
    <th>Object</th>
    <th>Count</th>
    <th>Object Name</th>
    <th>Culture</th>
    <th>Collection Place</th>
    <th>Ethnographic File Code</th>
    </tr>"""
    for o in objs:
        html += '''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>''' % (o[3], o[5], o[4], o[7], o[6], o[9])

    html += """<tr><td align="center" colspan="6"></td></tr>"""
    html += """<tr><td align="center" colspan="6"><b>%s objects</b></td></tr>""" % len(objs)
    html += """<tr><td align="center" colspan="6">"""
    html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td></tr>'''

    return html

def listSearchResults(authority, config, displaytype, form, rows):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    hasDups = False

    rows = sorted(rows, key=lambda tup: tup[0])
    rowcount = len(rows)

    label = authority
    if label[-1] == 's' and rowcount == 1: label = label[:-1]
    if label == 'taxon' and rowcount > 1: label = 'taxa'

    if displaytype == 'silent':
        html += """<table>"""
    elif displaytype == 'select':
        html += """<div style="float:left; width: 300px;">%s %s in this range</th>""" % (rowcount, label)
    else:
        if updateType == 'barcodeprint':
            rows.reverse()
            count = 0
            objectsHandled = []
            for r in rows:
                objects = cswaDB.getlocations(r[0], '', 1, config, updateType,institution)
                for o in objects:
                    if o[3] + o[4] in objectsHandled:
                        objects.remove(o)
                    else:
                        objectsHandled.append(o[3] + o[4])
                count += len(objects)
            html += """
    <table width="100%%">
    <tr>
      <th>%s %s and %s objects in this range</th>
    </tr>""" % (rowcount, label, count)
        else:
            html += """
    <table width="100%%">
    <tr>
      <th>%s %s in this range</th>
    </tr>""" % (rowcount, label)

    if rowcount == 0:
        html += "</table>"
        return hasDups, html

    if displaytype == 'select':
        html += """<li><input type="checkbox" name="select-%s" id="select-%s" checked/> select all</li>""" % (
            authority, authority)

    if displaytype == 'list' or displaytype == 'select':
        rowtype = 'location'
        if displaytype == 'select': rowtype = 'select'
        duplicates = []
        for r in rows:
            if r[1] in duplicates:
                hasDups = True
            else:
                duplicates.append(r[1])
                pass
            html += formatRow({'boxtype': authority, 'rowtype': rowtype, 'data': r}, form, config)

    elif displaytype == 'nolist':
        label = authority
        if label[-1] == 's': label = label[:-1]
        if rowcount == 1:
            html += '<tr><td class="authority">%s</td></tr>' % (rows[0][0])
        else:
            html += '<tr><th>first %s</th><td class="authority">%s</td></tr>' % (label, rows[0][0])
            html += '<tr><th>last %s</th><td class="authority">%s</td></tr>' % (label, rows[-1][0])

    if displaytype == 'select':
        html += "\n</div>"
    else:
        html += "</table>"
        #html += """<input type="hidden" name="count" value="%s">""" % rowcount

    return hasDups, html


def doGroupSearch(form, config, displayType):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    if form.get('gr.group') == '':
        return '<h3 class="error">Please enter group identifier!</h3>'

    if updateType == "barcodeprint":
        updateType = 'packinglist'
    else:
        updateType = 'objinfo'

    rows, msg = cswaDB.getgrouplist(form.get("gr.group"), 3000, config)

    if len(rows) == 0:
        return '<h3 class="error">No objects in this group! Sorry!</h3>'
    else:
        totalobjects = 0
        if updateType == 'objinfo':
            html += cswaConstants.infoHeaders(form.get('fieldset'))
        else:
            html += cswaConstants.getHeader(updateType,institution)
        for r in rows:
            totalobjects += 1
            html += formatRow({'rowtype': updateType, 'data': r}, form, config)

        html += '\n</table><table width="100%"'
        html += """<tr><td align="center" colspan="3">"""
        msg = "Caution: clicking on the button at left will update <b>ALL %s objects</b> shown on this page!" % totalobjects
        html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="3">%s</td></tr>''' % msg
        html += "\n</table>"

    return html

def doEnumerateObjects(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    try:
        locationList = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), MAXLOCATIONS, config)
    except:
        raise

    rowcount = len(locationList)

    if rowcount == 0:
        return '<h2>No locations in this range!</h2>'


    if updateType == 'keyinfo' or updateType == 'objinfo':
        html += cswaConstants.infoHeaders(form.get('fieldset'))
    else:
        html += cswaConstants.getHeader(updateType,institution)
    totalobjects = 0
    totallocations = 0
    for l in locationList:

        try:
            objects = cswaDB.getlocations(l[0], '', 1, config, updateType,institution)
        except:
            raise

        rowcount = len(objects)
        locations = {}
        if rowcount == 0:
            locationheader = formatRow({'rowtype': 'subheader', 'data': l}, form, config)
            locations[locationheader] = ['<tr><td colspan="3">No objects found at this location.</td></tr>']
        for r in objects:
            locationheader = formatRow({'rowtype': 'subheader', 'data': r}, form, config)
            if locationheader in locations:
                pass
            else:
                locations[locationheader] = []
                totallocations += 1

            totalobjects += 1
            locations[locationheader].append(formatRow({'rowtype': updateType, 'data': r}, form, config))

        locs = sorted(locations.keys())
        for header in locs:
            html += header
            html += '\n'.join(locations[header])


    html += "\n</table>\n"
    if totalobjects == 0:
        pass
    else:
        html += ""
        html += '\n<table width="100%">\n'
        html += """<tr><td align="center" colspan="3">"""
        if updateType == 'keyinfo' or updateType == 'objinfo':
            msg = "Caution: clicking on the button at left will revise the above fields for <b>ALL %s objects</b> shown in these %s locations!" % (
                totalobjects, totallocations)
        else:
            msg = "Caution: clicking on the button at left will change the " + updateType + " of <b>ALL %s objects</b> shown in these %s locations!" % (
                totalobjects, totallocations)
        html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="4">%s</td></tr>''' % msg
        html += "\n</table>"

    return html


def verifyLocation(loc, form, config):
    if loc == '':
        return
    location = cswaDB.getloclist('exact', loc, '', 1, config)
    if location == [] : return
    if loc == location[0][0]:
        return loc
    else:
        return ''

def doCheckMove(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    crate = verifyLocation(form.get("lo.crate"), form, config)
    fromLocation = verifyLocation(form.get("lo.location1"), form, config)
    toLocation = verifyLocation(form.get("lo.location2"), form, config)

    toRefname = cswaDB.getrefname('locations_common', toLocation, config)

    #sys.stderr.write('%-13s:: %-18s:: %s\n' % (updateType, 'toRefName', toRefname))

    # DEBUG
    #html += '<table cellpadding="8px" border="1">'
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('From',fromLocation)
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('Crate',crate)
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('To',toLocation)
    #html += '</table>'

    if crate == '':
        html += '<span class="error">Crate is not valid! Sorry!</span><br/>'
    if fromLocation == '':
        html += '<span class="error">From location is not valid! Sorry!</span><br/>'
    if toLocation == '':
        html += '<span class="error">To location is not valid! Sorry!</span><br/>'
    if crate == '' or fromLocation == '' or toLocation == '':
        return html

    try:
        # NB: the movecrate webapp uses the inventory query...naturally!
        objects = cswaDB.getlocations(form.get("lo.location1"), '', 1, config, 'inventory',institution)
    except:
        raise

    locations = {}
    if len(objects) == 0:
        return '<h3 class="error">No objects found at this location! Sorry!</h3>'

    totalobjects = 0
    totallocations = 0

    #sys.stderr.write('%-13s:: %s :: %-18s:: %s\n' % (updateType, crate, 'objects', len(objects)))
    for r in objects:
        if r[15] != crate: # skip if this is not the crate we want
            continue
        #sys.stderr.write('%-13s:: %-18s:: %s\n' % (updateType,  r[15],  r[0]))
        locationheader = formatRow({'rowtype': 'subheader', 'data': r}, form, config)
        if locationheader in locations:
            pass
        else:
            locations[locationheader] = []
            totallocations += 1

        totalobjects += 1
        locations[locationheader].append(formatRow({'rowtype': 'inventory', 'data': r}, form, config))

    locs = sorted(locations.keys())

    if len(locs) == 0:
        return '<span class="error">Did not find this crate at this location! Sorry!</span>'

    html += cswaConstants.getHeader(updateType,institution)
    for header in locs:
        html += header
        html += '\n'.join(locations[header])

    html += """<tr><td align="center" colspan="6"><td></tr>"""
    html += """<tr><td align="center" colspan="3">"""
    msg = "Caution: clicking on the button at left will move <b>ALL %s objects</b> shown in this crate!" % totalobjects
    html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="3">%s</td></tr>''' % msg

    html += "\n</table>"
    html += '<input type="hidden" name="toRefname" value="%s">' % toRefname
    html += '<input type="hidden" name="toLocAndCrate" value="%s: %s">' % (toLocation, crate)

    return html


def doCheckGroupMove(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)

    if form.get('gr.group') == '':
        return'<h3>Please enter group identifier!</h3>'

    toLocation = verifyLocation(form.get("lo.location"), form, config)
    toRefname = cswaDB.getrefname('locations_common', toLocation, config)

    if toLocation is None:
        return '<h3 class="error">Please enter a valid storage location!</h3>'

    try:
        objects, msg = cswaDB.getgrouplist(form.get("gr.group"), 3000, config)
    except:
        raise

    locations = []
    if len(objects) == 0:
        return '<h3 class="error">No objects found for this group! Sorry!</h3>'

    totalobjects = 0

    # sys.stderr.write('%-13s:: %s :: %-18s:: %s\n' % (updateType, crate, 'objects', len(objects)))
    for r in objects:
        # sys.stderr.write('%-13s:: %-18s:: %s\n' % (updateType,  r[3],  r[0]))
        # swap these two elements: getgrouplist and getlocations return slightly different sets.
        x = r[4]
        r[4] = r[5]
        r[5] = x
        totalobjects += 1
        locations.append(formatRow({'rowtype': 'powermove', 'data': r}, form, config))

    html += cswaConstants.getHeader('powermove', institution)
    html += """<tr><td align="center" colspan="6"><td></tr>"""
    html += '\n'.join(locations)
    html += """<tr><td align="center" colspan="6"><td></tr>"""
    html += """<tr><td align="center" colspan="3">"""
    msg = "Caution: clicking on the button at left will move <b>ALL %s objects</b> shown for this group!" % totalobjects
    html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="3">%s</td></tr>''' % msg

    html += "\n</table>"
    html += '<input type="hidden" name="toRefname" value="%s">' % toRefname
    html += '<input type="hidden" name="toLocAndCrate" value="%s">' % (toLocation)
    html += '<input type="hidden" name="toCrate" value="%s">' % ''

    return html


def doCheckPowerMove(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    crate1 = verifyLocation(form.get("lo.crate1"), form, config)
    crate2 = verifyLocation(form.get("lo.crate2"), form, config)

    if crate1 == '':
        html += '<span class="error">From Crate is not valid! Sorry!</span><br/>'
    if crate2 == '':
        html += '<span class="error">To Crate is not valid! Sorry!</span><br/>'

    fromLocation = verifyLocation(form.get("lo.location1"), form, config)
    toLocation = verifyLocation(form.get("lo.location2"), form, config)

    if fromLocation == '':
        html += '<span class="error">From location is not valid! Sorry!</span><br/>'
    if toLocation == '':
        html += '<span class="error">To location is not valid! Sorry!</span><br/>'
    if fromLocation == '' or toLocation == '':
        return html

    toLocRefname = cswaDB.getrefname('locations_common', toLocation, config)
    toCrateRefname = cswaDB.getrefname('locations_common', crate2, config)
    fromRefname = cswaDB.getrefname('locations_common', fromLocation, config)

    #sys.stderr.write('%-13s:: %-18s:: %s\n' % (updateType, 'toRefName', toRefname))

    # DEBUG
    #html += '<table cellpadding="8px" border="1">'
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('From',fromLocation)
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('Crate',crate)
    #html += '<tr><td>%s</td><td>%s</td></tr>' % ('To',toLocation)
    #html += '</table>'

    try:
        # NB: the movecrate webapp uses the inventory query...naturally!
        objects = cswaDB.getlocations(form.get("lo.location1"), '', 1, config, 'inventory',institution)
    except:
        raise

    locations = {}
    if len(objects) == 0:
        return '<h3 class="error">No objects found at this location! Sorry!</h3>'

    totalobjects = 0
    totallocations = 0

    #sys.stderr.write('%-13s:: %s :: %-18s:: %s\n' % (updateType, crate, 'objects', len(objects)))
    for r in objects:
        if r[15] != crate1 and crate1 != '': # skip if this is not the crate we want
                continue
        #sys.stderr.write('%-13s:: %-18s:: %s\n' % (updateType,  r[15],  r[0]))
        locationheader = formatRow({'rowtype': 'subheader', 'data': r}, form, config)
        if locationheader in locations:
            pass
        else:
            locations[locationheader] = []
            totallocations += 1

        totalobjects += 1
        locations[locationheader].append(formatRow({'rowtype': 'powermove', 'data': r}, form, config))

    locs = sorted(locations.keys())

    if len(locs) == 0:
        return '<span class="error">Did not find this crate at this location! Sorry!</span>'

    html += cswaConstants.getHeader(updateType,institution)
    for header in locs:
        html += header
        html += '\n'.join(locations[header])

    html += """<tr><td align="center" colspan="6"><td></tr>"""
    html += """<tr><td align="center" colspan="3">"""
    msg = "Caution: clicking on the button at left will move <b>ALL %s objects</b> shown in this crate!" % totalobjects
    html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="3">%s</td></tr>''' % msg

    html += "\n</table>"
    if crate2 is None: crate2 = ''
    html += '<input type="hidden" name="toRefname" value="%s">' % toLocRefname
    html += '<input type="hidden" name="toLocAndCrate" value="%s: %s">' % (toLocation, crate2)
    html += '<input type="hidden" name="toCrate" value="%s">' % toCrateRefname

    return html

def getTrio(form, config):
    # If the group field has input, use that
    msg = ''
    if form.get("gr.group") != '':
        # sys.stderr.write('group: %s\n' % form.get("gr.group"))
        objs, msg = cswaDB.getgrouplist(form.get("gr.group"), 5000, config)
    # If the museum number field has input, html += by object
    elif form.get('ob.objno1') != '':
        objs, msg = cswaDB.getobjlist('range', form.get("ob.objno1"), form.get("ob.objno2"), 1000, config)
    elif form.get('ob.objno1') != 'lo.location1':
        rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), 500, config)
        objs = []
        seen = {}
        for r in rows:
            objects = cswaDB.getlocations(r[0], '', 1, config, 'keyinfo', 'pahma')
            for o in objects:
                if not (o[3] + o[4] in seen):
                    objs.append(o)
                    seen[o[3] + o[4]] = 1


    return objs, msg, len(objs)

def doBulkEdit(form, config):

    valid, error = validateParameters(form, config)
    if not valid: return error

    institution, updateType, updateactionlabel = basicSetup(form, config)

    objs, msg, totalobjects = getTrio(form, config)

    if totalobjects == 0:
        return '<h3 class="error">No objects found! Sorry!</h3>'

    CSIDs = []
    fieldset = form.get('fieldset')
    for row in objs:
        CSIDs.append(row[8])

    refNames2find = {}
    setRefnames(refNames2find, fieldset, form, config, 'user')

    return doTheUpdate(CSIDs, form, config, fieldset, refNames2find)


def doBulkEditForm(form, config, displaytype):
    html = ''

    valid, error = validateParameters(form, config)
    if not valid: return html + error

    institution, updateType, updateactionlabel = basicSetup(form, config)

    objs, msg, totalobjects = getTrio(form, config)

    if totalobjects == 0:
        return '<h3 class="error">No objects found! Sorry!</h3>'

    html += '''<table width="100%" cellpadding="8px"><tbody><tr class="smallheader">
      <td width="250px">Field</td>
      <td>Value to Set</td></tr>'''

    html += formatInfoReviewForm(form)

    html += '</table>'
    html += '<table>'

    msg = "Caution: clicking on the button at left will update <b>ALL %s objects</b> in this range!" % totalobjects
    html += """<tr><td align="center" colspan="3"></tr>"""
    html += """<tr><td align="center" colspan="2">"""
    html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td  colspan="1">%s</td></tr>''' % msg


    html += '</table>'
    html += ""

    return html


def doCreateObjects(form, config):
    html = ''

    institution, updateType, updateactionlabel = basicSetup(form, config)
    msgs = []

    html += '''<table width="100%" cellpadding="8px"><tbody><tr class="smallheader">
      <td>Item</td><td>Value</td>'''

    year, msg = getints('create.year', form)
    if msg != '': msgs.append(msg)
    accession, msg = getints('create.accession', form)
    if msg != '': msgs.append(msg)
    sequence, msg = getints('create.sequence', form)
    if msg != '': msgs.append(msg)
    count, msg = getints('create.count', form)
    if msg != '': msgs.append(msg)

    try:
        startsortobject = '%0.10d.%0.10d.%0.10d' % (year, accession, sequence)
        startobject = '%s.%s.%s' % (year, accession, sequence)
    except:
        startobject = 'invalid'
        msgs.append('start object value invalid')

    try:
        endsortobject = '%0.10d.%0.10d.%0.10d' % (year, accession, sequence + count - 1)
        endobject = '%s.%s.%s' % (year, accession, sequence + count - 1)
    except:
        endobject = 'invalid'
        msgs.append('end object value invalid')

    try:
        objs = cswaDB.getlistofobjects('range', startsortobject, endsortobject, 100, config)
        totalobjects = len(objs)
        if totalobjects != 0:
            msgs.append('there are already %s objects in this range!' % totalobjects)
            msgs.append('(%s to %s)' % (startobject, endobject))
            for o in objs:
                msgs.append(o[0])
    except:
        msgs.append('problem checking object range')
        totalobjects = -1

    if count > 100:
        msgs.append('Maximum objects you can create at one time is 100.')
        msgs.append('Consider breaking your work into chunks of 100.')

    if len(msgs) == 0:
        html += "<tr><td>%s</td><td>%s</td></tr>" % ('first object', startobject)
        html += "<tr><td>%s</td><td>%s</td></tr>" % ('last object', endobject)
        html += "<tr><td>%s</td><td>%s</td></tr>" % ('objects requested', count)

        if form.get('action') == config.get('info', 'updateactionlabel'):
            # create objects here
            for seq in range(count):
                objectNumber = '%s.%s.%s' % (year, accession, sequence + seq)
                sortableobjectnumber = '%0.10d.%0.10d.%0.10d' % (year, accession, sequence + seq)
                objectinfo = {'objectNumber': objectNumber}
                objectinfo['sortableObjectNumber'] = sortableobjectnumber
                message,csid = createObject(objectinfo, config, form)
                html += "<tr><td>%s</td><td>%s</td></tr>" % (objectNumber, csid)
            html += "<tr><td>%s</td><td>%s</td></tr>" % ('created objects', count)
        else:
            # list objects to be created
            msg = "Caution: clicking on the button at left will create <b> %s empty objects</b>!" % count
            html += """<tr><td align="center" colspan="3"></tr>"""
            html += """<tr><td align="center" colspan="2">"""
            html += '''<input type="submit" class="save" value="''' + updateactionlabel + '''" name="action"></td><td colspan="1">%s</td></tr>''' % msg

    else:
        for m in msgs:
            html += '<tr><td class="error">%s</td><td></td></tr>' % m

    html += '</table>'
    html += ""

    return html


def doUpdateKeyinfo(form, config):
    html = ''

    #html += form
    CSIDs = []
    fieldset = form.get('fieldset')
    for i in form:
        if 'csid.' in i:
            CSIDs.append(form.get(i))

    refNames2find = {}
    for row, csid in enumerate(CSIDs):

        index = csid # for now, the index is the csid
        setRefnames(refNames2find, fieldset, form, config, index)

    return doTheUpdate(CSIDs, form, config, fieldset, refNames2find)


def doTheUpdate(CSIDs, form, config, fieldset, refNames2find):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)

    html += cswaConstants.getHeader('keyinfoResult',institution)

    numUpdated = 0
    for row, csid in enumerate(CSIDs):

        if updateType == 'bulkedit':
            index = 'user'
        else:
            index = csid
        updateItems = {}
        updateItems['objectCsid'] = csid
        updateItems['objectName'] = form.get('onm.' + index)
        updateItems['objectNumber'] = form.get('oox.' + index)
        if fieldset == 'namedesc':
            updateItems['briefDescription'] = form.get('bdx.' + index)
        elif fieldset == 'registration':
            updateItems['pahmaAltNum'] = form.get('anm.' + index)
            updateItems['pahmaAltNumType'] = form.get('ant.' + index)
            updateItems['fieldCollector'] = refNames2find[form.get('cl.' + index)]
            updateItems['pahmaObjectStatus'] = form.get('obs.' + index)
        elif fieldset == 'keyinfo':
            if form.get('ocn.' + index) != '':
                updateItems['objectCount'] = form.get('ocn.' + index)
            updateItems['pahmaFieldCollectionPlace'] = refNames2find[form.get('cp.' + index)]
            updateItems['assocPeople'] = refNames2find[form.get('cg.' + index)]
            updateItems['pahmaEthnographicFileCode'] = refNames2find[form.get('fc.' + index)]
        elif fieldset == 'hsrinfo':
            if form.get('ocn.' + index) != '':
                updateItems['objectCount'] = form.get('ocn.' + index)
            updateItems['inventoryCount'] = form.get('ctn.' + index)
            updateItems['pahmaFieldCollectionPlace'] = refNames2find[form.get('cp.' + index)]
            updateItems['briefDescription'] = form.get('bdx.' + index)
        elif fieldset == 'objtypecm':
            if form.get('ocn.' + index) != '':
                updateItems['objectCount'] = form.get('ocn.' + index)
            updateItems['collection'] = form.get('ot.' + index)
            updateItems['responsibleDepartment'] = form.get('cm.' + index)
            updateItems['pahmaFieldCollectionPlace'] = refNames2find[form.get('cp.' + index)]
            updateItems['pahmaTmsLegacyDepartment'] = form.get('ld.' + index)
            updateItems['pahmaObjectStatus'] = form.get('obs.' + index)
        elif fieldset == 'placeanddate':
            updateItems['pahmaFieldLocVerbatim'] = form.get('vfcp.' + index)
            updateItems['pahmaFieldCollectionDate'] = form.get('dcol.' + index)
        elif fieldset == 'places':
            updateItems['pahmaFieldLocVerbatim'] = form.get('vfcp.' + index)
            updateItems['pahmaFieldCollectionPlace'] = refNames2find[form.get('cp.' + index)]
            updateItems['objectProductionPlace'] = refNames2find[form.get('pp.' + index)]
            updateItems['contentPlace'] = refNames2find[form.get('pd.' + index)]
        elif fieldset == 'dates':
            updateItems['objectProductionDate'] = form.get('dprd.' + index)
            updateItems['pahmaFieldCollectionDate'] = form.get('dcol.' + index)
            updateItems['contentDate'] = form.get('ddep.' + index)
            updateItems['briefDescription'] = form.get('bdx.' + index)
        elif fieldset == 'mattax':
            updateItems['material'] = refNames2find[form.get('ma.' + index)]
            updateItems['taxon'] = refNames2find[form.get('ta.' + index)]
            updateItems['briefDescription'] = form.get('bdx.' + index)
        elif fieldset == 'student':
            updateItems['taxon'] = refNames2find[form.get('ta.' + index)]
            updateItems['fieldLocCountry'] = refNames2find[form.get('cn.' + index)]
            updateItems['fieldLocState'] = refNames2find[form.get('st.' + index)]
            updateItems['fieldLocCounty'] = refNames2find[form.get('co.' + index)]
            updateItems['numberValue'] = form.get('pc.' + index)
            # updateItems['briefDescription'] = form.get('bdx.' + index)
        elif fieldset == 'fullmonty':
            if form.get('ocn.' + index) != '':
                updateItems['objectCount'] = form.get('ocn.' + index)
            updateItems['briefDescription'] = form.get('bdx.' + index)

            updateItems['assocPeople'] = refNames2find[form.get('cg.' + index)]
            updateItems['collection'] = form.get('ot.' + index)
            updateItems['contentDate'] = form.get('ddep.' + index)
            updateItems['contentPlace'] = refNames2find[form.get('pd.' + index)]
            updateItems['fieldCollector'] = refNames2find[form.get('cl.' + index)]
            updateItems['inventoryCount'] = form.get('ctn.' + index)
            updateItems['material'] = refNames2find[form.get('ma.' + index)]
            updateItems['objectProductionDate'] = form.get('dprd.' + index)
            updateItems['objectProductionPlace'] = refNames2find[form.get('pp.' + index)]
            updateItems['pahmaObjectStatus'] = form.get('obs.' + index)
            updateItems['pahmaAltNum'] = form.get('anm.' + index)
            updateItems['pahmaAltNumType'] = form.get('ant.' + index)
            updateItems['pahmaEthnographicFileCode'] = refNames2find[form.get('fc.' + index)]
            updateItems['pahmaFieldLocVerbatim'] = form.get('vfcp.' + index)
            updateItems['pahmaFieldCollectionDate'] = form.get('dcol.' + index)
            updateItems['pahmaFieldCollectionPlace'] = refNames2find[form.get('cp.' + index)]
            updateItems['pahmaTmsLegacyDepartment'] = form.get('ld.' + index)
            updateItems['objectProductionPerson'] = refNames2find[form.get('pe.' + index)]
            updateItems['responsibleDepartment'] = form.get('cm.' + index)
            updateItems['taxon'] = refNames2find[form.get('ta.' + index)]

        else:
            pass
            #error!

        for i in ('handlerRefName',):
            updateItems[i] = form.get(i)

        #html += updateItems
        msg = ''
        if fieldset in ['keyinfo', 'fullmonty']:
            if updateItems['pahmaFieldCollectionPlace'] == '' and form.get('cp.' + index):
                if form.get('cp.' + index) == cswaDB.getCSIDDetail(config, index, 'fieldcollectionplace'):
                    pass
                else:
                    msg += '<span class="error"> Field Collection Place: term "%s" not found, field not updated.</span>' % form.get('cp.' + index)
            if updateItems['assocPeople'] == '' and form.get('cg.' + index):
                if form.get('cg.' + index) == cswaDB.getCSIDDetail(config, index, 'assocpeoplegroup'):
                    pass
                else:
                    msg += '<span class="error"> Cultural Group: term "%s" not found, field not updated.</span>' % form.get('cg.' + index)
            if updateItems['pahmaEthnographicFileCode'] == '' and form.get('fc.' + index):
                msg += '<span class="error"> Ethnographic File Code: term "%s" not found, field not updated.</span>' % form.get('fc.' + index)
            if 'objectCount' in updateItems:
                try:
                    int(updateItems['objectCount'])
                    int(updateItems['objectCount'][0])
                except ValueError:
                    msg += '<span class="error"> Object count: "%s" is not a valid number!</span>' % form.get('ocn.' + index)
                    del updateItems['objectCount']
        if fieldset in ['registration', 'fullmonty']:
            if updateItems['fieldCollector'] == '' and form.get('cl.' + index):
                msg += '<span class="error"> Field Collector: term "%s" not found, field not updated.</span>' % form.get('cl.' + index)
        if fieldset in ['hsrinfo', 'fullmonty']:
            if updateItems['pahmaFieldCollectionPlace'] == '' and form.get('cp.' + index):
                if form.get('cp.' + index) == cswaDB.getCSIDDetail(config, index, 'fieldcollectionplace'):
                    pass
                else:
                    msg += '<span class="error"> Field Collection Place: term "%s" not found, field not updated.</span>' % form.get('cp.' + index)
            if 'objectCount' in updateItems:
                try:
                    int(updateItems['objectCount'])
                    int(updateItems['objectCount'][0])
                except ValueError:
                    msg += '<span class="error"> Object count: "%s" is not a valid number!</span>' % form.get('ocn.' + index)
                    del updateItems['objectCount']
        if fieldset in ['objtypecm', 'fullmonty']:
            if updateItems['pahmaFieldCollectionPlace'] == '' and form.get('cp.' + index):
                if form.get('cp.' + index) == cswaDB.getCSIDDetail(config, index, 'fieldcollectionplace'):
                    pass
                else:
                    msg += '<span class="error"> Field Collection Place: term "%s" not found, field not updated.</span>' % form.get('cp.' + index)
            if 'objectCount' in updateItems:
                try:
                    int(updateItems['objectCount'])
                    int(updateItems['objectCount'][0])
                except ValueError:
                    msg += '<span class="error"> Object count: "%s" is not a valid number!</span>' % form.get('ocn.' + index)
                    del updateItems['objectCount']
        if fieldset in ['mattax', 'fullmonty']:
            if updateItems['material'] == '' and form.get('ma.' + index):
                msg += '<span class="error"> Materials: term "%s" not found, field not updated.</span>' % form.get('ma.' + index)
            if updateItems['taxon'] == '' and form.get('ta.' + index):
                msg += '<span class="error"> Taxon: term "%s" not found, field not updated.</span>' % form.get('ta.' + index)
        if fieldset in ['placeanddate', 'fullmonty']:
            # msg += 'place and date'
            pass

        newItems = {}
        for item in updateItems.keys():
            newItems[item] = updateItems[item]
            if updateItems[item] == 'None' or updateItems[item] is None:
                if item in 'collection inventoryCount objectCount'.split(' '):
                    del newItems[item]
                    #updateMsg += 'deleted %s <br/>' % item
                else:
                    newItems[item] = ''
                    #updateMsg += 'eliminated %s <br/>' % item
            else:
                #updateMsg += 'kept %s, value: %s <br/>' % (item, updateItems[item])
                pass
        updateItems = newItems

        try:
            #pass
            when2post, updateMsg  = updateCspace(fieldset, updateItems, form, config)
            if updateMsg != '':
                msg = '<span class="warning">%s</span>' % updateMsg
            if not 'ERROR' in updateMsg:
                numUpdated += 1
        except:
            raise

        msg = '%sd. %s' % (when2post, msg)
        html += ('<tr>' + (3 * '<td class="ncell">%s</td>') + '</tr>\n') % (makeObjectLink(config, csid, updateItems['objectNumber']), msg, updateItems['objectCsid'])

    html += "\n</table>"
    html += '<h4 style="margin-top: 20px;">%s of %s objects had information updated</h4>' % (numUpdated, row + 1)

    return html


def doUpdateLocations(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    #notlocated = config.get('info','notlocated')
    if institution == 'bampfa':
        notlocated = "urn:cspace:bampfa.cspace.berkeley.edu:locationauthorities:name(location):item:name(x781)'Not Located'"
    else:
        notlocated = "urn:cspace:pahma.cspace.berkeley.edu:locationauthorities:name(location):item:name(sl23524)'Not located'"
    updateValues = [form.get(i) for i in form if 'r.' in i and not 'gr.' in i]

    # if reason is a refname (e.g. bampfa), extract just the displayname
    reason = form.get('reason')
    reason = re.sub(r"^urn:.*'(.*)'", r'\1', reason)

    Now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # Now = midnight local time for locations...
    # Now = datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")

    html += cswaConstants.getHeader('inventoryResult',institution)

    numUpdated = 0
    for row, object in enumerate(updateValues):

        updateItems = {}
        cells = object.split('|')
        updateItems['objectStatus'] = cells[0]
        updateItems['objectCsid'] = cells[1]
        objectCsid = cells[1]
        updateItems['locationRefname'] = cells[2]
        updateItems['subjectCsid'] = '' # cells[3] is actually the csid of the movement record for the current location; the updated value gets inserted later
        updateItems['objectNumber'] = cells[4]
        updateItems['crate'] = cells[5]
        updateItems['inventoryNote'] = form.get('n.' + cells[4]) if form.get('n.' + cells[4]) else ''
        updateItems['locationDate'] = Now
        updateItems['computedSummary'] = updateItems['locationDate'][0:10] + (' (%s)' % reason)

        for i in ('handlerRefName', 'reason'):
            updateItems[i] = form.get(i)

        # ugh...this logic is in fact rather complicated...
        msg = 'location updated.'
        # if we are moving a crate, use the value of the toLocation's refname, which is stored hidden on the form.
        if updateType == 'movecrate':
            updateItems['locationRefname'] = form.get('toRefname')
            msg = 'crate moved to %s.' % form.get('toLocAndCrate')

        if updateType in ['moveobject', 'powermove', 'grpmove']:
            if updateItems['objectStatus'] == 'do not move':
                msg = "not moved."
            else:
                updateItems['locationRefname'] = form.get('toRefname')
                updateItems['crate'] = form.get('toCrate')
                msg = 'object moved to %s.' % form.get('toLocAndCrate')


        if updateItems['objectStatus'] == 'not found':
            updateItems['locationRefname'] = notlocated
            updateItems['crate'] = ''
            msg = "moved to 'Not Located'."
        try:
            if "not moved" in msg:
                pass
            else:
                updateLocations(updateItems, config, form)
                numUpdated += 1
        except:
            msg = '<span class="error">location update failed!</span>'
        html += ('<tr>' + (4 * '<td class="ncell">%s</td>') + '</tr>\n') % (
            makeObjectLink(config, objectCsid, updateItems['objectNumber']), updateItems['objectStatus'], updateItems['inventoryNote'], msg)

    html += "\n</table>"
    html += '<h4 style="margin-top: 20px">%s of %s objects had movements recorded</h4>' % (numUpdated, row + 1)

    return html


def doPackingList(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    if form.get('groupbyculture') is not None:
        updateType = 'packinglistbyculture'

    place = form.get("cp.place")
    if place != None and place != '':
        places = cswaGetAuthorityTree.getAuthority('places',  'Placeitem', place,  config.get('connect', 'connect_string'))
        places = [p[0] for p in places]
    else:
        places = []

    #[sys.stderr.write('packing list place term: %s\n' % x) for x in places]
    try:
        locationList = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), MAXLOCATIONS,
                                         config)
    except:
        raise

    rowcount = len(locationList)

    #[sys.stderr.write('packing list locations : %s\n' % x[0]) for x in locationList]

    if rowcount == 0:
        return'<tr><td width="500px"><h2>No locations in this range!</h2></td></tr>'

    html += cswaConstants.getHeader(updateType,institution)
    totalobjects = 0
    totallocations = 0
    locations = {}
    for l in locationList:

        try:
            objects = cswaDB.getlocations(l[0], '', 1, config, 'packinglist',institution)
        except:
            raise

        #[sys.stderr.write('packing list objects: %s\n' % x[3]) for x in objects]
        rowcount = len(objects)
        if rowcount == 0:
            if updateType != 'packinglistbyculture':
                locationheader = formatRow({'rowtype': 'subheader', 'data': l}, form, config)
                locations[locationheader] = ['<tr><td colspan="3">No objects found at this location.</td></tr>']
        for r in objects:
            if checkObject(places, r):
                totalobjects += 1
                if updateType == 'packinglistbyculture':
                    temp = copy.deepcopy(r)
                    cgrefname = r[11]
                    parentcount = 0
                    if cgrefname is not None:
                        parents = cswaDB.findparents(cgrefname, config)
                        #[sys.stderr.write('term: %s' % x) for x in parents]
                        if parents is None or len(parents) == 1:
                            subheader = 'zzzNo parent :: %s' % r[7]
                        else:
                            subheader = [term[0] for term in parents]
                            subheader = ' :: '.join(subheader)
                            parentcount = len(parents)
                    else:
                        subheader = 'zzzNo cultural group specified'
                        #sys.stderr.write('%s %s' % (str(r[7]), parentcount))
                    temp[0] = subheader
                    temp[7] = r[0]
                    r = temp
                    locationheader = formatRow({'rowtype': 'subheader', 'data': r}, form, config)
                else:
                    locationheader = formatRow({'rowtype': 'subheader', 'data': r}, form, config)
                if locationheader in locations:
                    pass
                else:
                    locations[locationheader] = []
                    totallocations += 1

                locations[locationheader].append(formatRow({'rowtype': updateType, 'data': r}, form, config))

    locs = sorted(locations.keys())
    for header in locs:
        html += header.replace('zzz', '')
        html += '\n'.join(locations[header])
        html += """<tr><td align="center" colspan="6">&nbsp;</tr>"""
    html += """<tr><td align="center" colspan="6"><td></tr>"""
    headingtypes = 'cultures' if updateType == 'packinglistbyculture' else 'including crates'
    html += """<tr><td align="center" colspan="6">Packing list completed. %s objects, %s locations, %s %s</td></tr>""" % (
        totalobjects, len(locationList), totallocations, headingtypes)
    html += "\n</table>"

    return html


def doAuthorityScan(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    dead,rare,qualifier = setFilters(form)

    if updateType == 'locreport':
        Taxon = form.get("ut.taxon")
        if Taxon != None:
            dummy1, dummy2, Taxa = listAuthorities('taxon', 'TaxonTenant35', Taxon, config, form, 'list')
        else:
            Taxa = []
        tList = [t[0] for t in Taxa]
        column = 1

    elif updateType == 'holdings':
        Place = form.get("px.place")
        if Place != None:
            dummy1, dummy2, Places = listAuthorities('places', 'Placeitem', Place, config, form, 'silent')
        else:
            Places = []
        tList = [t[0] for t in Places]
        column = 5

    try:
        objects = cswaDB.getplants('', '', 1, config, 'getalltaxa', qualifier)
    except:
        raise

    rowcount = len(objects)

    if rowcount == 0:
        return '<h2>No plants in this range!</h2>'

    html += cswaConstants.getHeader(updateType,institution)
    counts = {}
    statistics = { 'Total items': 'totalobjects',
                   'Accessions': 0,
                   'Unique taxonomic names': 1,
                   'Unique species': 'species',
                   'Unique genera': 'genus'
    }
    for s in statistics.keys():
        counts[s] = Counter()

    totalobjects = 0
    for t in objects:
        if t[column] in tList:
            if updateType in ['locreport','holdings'] and checkMembership(t[7], rare) and checkMembership(t[8], dead):
                if t[8] == 'true' or t[8] is None:
                    t[3] = "%s [%s]" % (t[13],t[12])
                else:
                    pass
                html += formatRow({'rowtype': updateType, 'data': t}, form, config)
                totalobjects += 1
                countStuff(statistics,counts,t,totalobjects)

    html += "\n</table>"

    return html


def downloadCsv(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)

    try:
        # create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        filename = '%s_%s.csv' % (updateType, datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        #html += 'Content-type: application/octet-stream; charset=utf-8'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    except:
        html += 'Problem creating .csv file. Sorry!'
        return html

    if updateType == 'governmentholdings':
        try:
            query = cswaDB.getDisplayName(config, form.get('agency'))
            if query is None:
                return '<h3 class="error">Please Select An Agency</h>'
            sites = cswaDB.getSitesByOwner(config, form.get('agency'))
        except:
            return '<h3 class="error">Problem. Did you select an agency?</h>'

        for s in sites:
                writer.writerow((s[0], s[1], s[2], s[3]))

    else:
        try:
            rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), 500, config)
        except:
            return '<h3 class="error">Problem. Did you select valid values for location range?</h>'

        place = form.get("cp.place")
        if place != None and place != '':
            places = cswaGetAuthorityTree.getAuthority('places',  'Placeitem', place,  config.get('connect', 'connect_string'))
        else:
            places = []

        #rowcount = len(rows)

        for r in rows:
            objects = cswaDB.getlocations(r[0], '', 1, config, 'keyinfo', institution)
            #[sys.stderr.write('packing list csv objects: %s\n' % x[3]) for x in objects]
            for o in objects:
                if checkObject(places, o):
                    if institution == 'bampfa':
                        writer.writerow([o[x] for x in [0, 1, 3, 4, 6, 7, 9]])
                    else:
                        writer.writerow([o[x] for x in [0, 2, 3, 4, 5, 6, 7, 9]])

    return response



def doBarCodes(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)

    action = form.get('action')

    valid, error = validateParameters(form, config)
    if not valid: return html + error

    if action == "Create Labels for Locations Only":
        html += cswaConstants.getHeader('barcodeprintlocations',institution)
    else:
        html += cswaConstants.getHeader(updateType,institution)

    totalobjects = 0
    #If the group field has input, use that
    if form.get("gr.group") != '':
        # sys.stderr.write('group: %s\n' % form.get("gr.group"))
        objs, msg = cswaDB.getgrouplist(form.get("gr.group"), 5000, config)
        if action == 'Create Labels for Objects':
            totalobjects += len(objs)
            o = [o[0:8] + [o[9]] for o in objs]
            labelFilename = writeCommanderFile('objectrange', form.get("printer"), 'objectLabels', 'objects', o, config)
            html += '<tr><td>%s</td><td>%s</td><tr><td colspan="4"><i>%s</i></td></tr>' % (
                'objectrange', len(o), labelFilename)
    #If the museum number field has input, html += by object
    elif form.get('ob.objno1') != '':
        objs, msg = cswaDB.getobjlist('range', form.get("ob.objno1"), form.get("ob.objno2"), 1000, config)

        if len(objs) == 0:
            return '<h3 class="error">No objects in this range! Sorry!</h3>'

        if action == 'Create Labels for Objects':
            totalobjects += len(objs)
            o = [o[0:8] + [o[9]] for o in objs]
            labelFilename = writeCommanderFile('objectrange', form.get("printer"), 'objectLabels', 'objects', o, config)
            html += '<tr><td>%s</td><td>%s</td><tr><td colspan="4"><i>%s</i></td></tr>' % (
                'objectrange', len(o), labelFilename)
    else:
        try:
            #If no end location, assume single location
            if form.get("lo.location2"):
                rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location2"), 500, config)
            else:
                rows = cswaDB.getloclist('range', form.get("lo.location1"), form.get("lo.location1"), 500, config)
        except:
            raise

        rowcount = len(rows)

        objectsHandled = []
        rows.reverse()
        if action == "Create Labels for Locations Only":
            labelFilename = writeCommanderFile('locations', form.get("printer"), 'locationLabels', 'locations', rows, config)
            html += '<tr><td>%s</td><td colspan="4"><i>%s</i></td></tr>' % (len(rows), labelFilename)
            html += "\n</table>"
            return html
        else:
            for r in rows:
                objects = cswaDB.getlocations(r[0], '', 1, config, updateType,institution)
                for o in objects:
                    if o[3] + o[4] in objectsHandled:
                        objects.remove(o)
                        html += '<tr><td>already printed a label for</td><td>%s</td><td>%s</td><td/></tr>' % (o[3], o[4])
                    else:
                        objectsHandled.append(o[3] + o[4])
                totalobjects += len(objects)
                # hack: move the ethnographic file code to the right spot for this app... :-(
                objects = [o[0:8] + [o[9]] for o in objects]
                labelFilename = writeCommanderFile(r[0], form.get("printer"), 'objectLabels', 'objects', objects, config)
                html += '<tr><td>%s</td><td>%s</td><td colspan="4"><i>%s</i></td></tr>' % (r[0], len(objects), labelFilename)

    html += """<tr><td align="center" colspan="4"><td></tr>"""
    html += """<tr><td align="center" colspan="4">"""
    if totalobjects != 0:
        if form.get('ob.objno1') or form.get('gr.group'):
            html += "<b>%s object barcode(s) printed." % totalobjects
        else:
            html += "<b>%s object(s)</b> found in %s locations." % (totalobjects, rowcount)
    else:
        return '<h3 class="error">No objects found in this range.</h3>'

    html += "\n</td></tr></table>"

    return html


def doAdvancedSearch(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    groupby = form.get('groupby')

    valid, error = validateParameters(form, config)
    if not valid: return html + error

    dead,rare,qualifier = setFilters(form)

    beds = [form.get(i) for i in form if 'locations.' in i]
    taxa = [form.get(i) for i in form if 'taxon.' in i]
    places = [form.get(i) for i in form if 'places.' in i]

    #taxa: column = 1
    #family: column = 2
    #beds: column = 3
    #place: column = 5

    try:
        objects = cswaDB.getplants('', '', 1, config, 'getalltaxa', qualifier)
    except:
        raise

    html += cswaConstants.getHeader(updateType,institution)
    #totalobjects = 0
    accessions = []
    for t in objects:
        if checkMembership(t[1], taxa) and checkMembership(t[3], beds) and checkMembership(t[5],
            places) and checkMembership(t[7], rare) and checkMembership(t[8], dead):
            html += formatRow({'rowtype': updateType, 'data': t}, form, config)

    html += """</table><table>"""
    html += """<tr><td align="center">&nbsp;</tr>"""
    html += """<tr><td align="center"></tr>"""
    html += """<tr><td align="center">Report completed. %s objects displayed</td></tr>""" % (len(accessions))
    html += "\n</table>"

    return html


def doBedList(form, config):
    html = ''
    institution, updateType, updateactionlabel = basicSetup(form, config)
    valid, error = validateParameters(form, config)
    if not valid: return html + error

    groupby = form.get('groupby')
    reporttype = form.get('reporttype')

    dead,rare,qualifier = setFilters(form)

    if updateType == 'bedlist':
        rows = [form.get(i) for i in form if 'locations.' in i]
    # currently, the location report does not call this function. but it might...
    elif updateType == 'locreport':
        rows = [form.get(i) for i in form if 'taxon.' in i]

    rowcount = len(rows)
    totalobjects = 0
    if groupby == 'none':
        html += cswaConstants.getHeader(f'{updateType}.{groupby}.{reporttype}', institution)
    else:
        html += '<table>'
    rows = sorted(rows)
    for headerid, l in enumerate(rows):

        try:
            objects = cswaDB.getplants(l, '', 1, config, updateType, qualifier)
        except:
            raise

        sys.stderr.write('%-13s:: %s\n' % (updateType, 'l=%s, q=%s, objects: %s' % (l,qualifier,len(objects))))
        if groupby == 'none':
            pass
        else:
            if len(objects) == 0:
                pass
            else:
                html += formatRow({'rowtype': 'subheader', 'data': [l, ]}, form, config)
                html += '<tr><td colspan="6">'
                html += cswaConstants.getHeader(f'{updateType}.{groupby}.{reporttype}', institution) % headerid

        for r in objects:
            #html += "<tr><td>%s<td>%s</tr>" % (len(places),r[6])
            # skip if the accession is not really in this location...
            #html += "<tr><td>loc = %s<td>this = %s</tr>" % (l,r[0])
            #if r[4] == '59.1168':
            #    html += "<tr><td>"
            #    html += r
            #    html += "</td></tr>"
            if (checkMembership(r[8],rare) and checkMembership(r[9],dead)) or r[12] == 'Dead':
                # nb: for bedlist, the gardenlocation (r[0]) is not displayed, so the next
                # few lines do not alter the display.
                if checkMembership(r[9],['dead']):
                    r[0] = "%s [%s]" % (r[10],r[12])
                r[0] = "%s = %s :: %s [%s]" % (r[9],r[0],r[10],r[12])
                totalobjects += 1
                html += formatRow({'rowtype': updateType, 'data': r}, form, config)

        if groupby == 'none':
            pass
        else:
            if len(objects) == 0:
                pass
            else:
                html += '</tbody></table></td></tr>'
                #html += """<tr><td align="center" colspan="6">&nbsp;</tr>"""

    if groupby == 'none':
        html += "\n</tbody></table>"
    else:
        html += '</table>'
    html += """<table><tr><td align="center"></tr>"""
    html += """<tr><td align="center">Bed List completed. %s objects, %s locations</td></tr>""" % (
        totalobjects, len(rows))
    html += "\n</table>"

    return html


def doHierarchyView(form, config):
    html = ''

    query = form.get('authority')
    if query == 'None':
        #hook
        return '<h3 class="error">Please select an authority!</h3>'

    res = cswaDB.gethierarchy(query, config)
    html += '<p></p><a class="prettyBtn" id="all">Toggle All</a><p/><div class="tree">'
    if res == []:
        return '<h3 class="error">Sorry, could not retrieve this authority hierarchy!</h3>'
    lookup = {concept.PARENT: concept.PARENT}
    link = ''
    hostname = config.get('connect', 'hostname')
    institution, updateType, updateactionlabel = basicSetup(form, config)
    port = ''
    protocol = 'https'
    if query == 'taxonomy':
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/taxon.html?csid=%s'
    elif query == 'places':
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/place.html?csid=%s'
    else:
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/concept.html?csid=%s&vocab=' + query
    for row in res:
        prettyName = row[0].replace('"', "'")
        if len(prettyName) > 0 and prettyName[0] == '@':
            #prettyName = '<' + prettyName[1:] + '> '
            prettyName = '<b>&lt;' + prettyName[1:] + '&gt;</b> '
        prettyName = '<a target="term" href="%s">%s</a>' % (link % (row[2]), prettyName)
        #prettyName = '<a>%s</a>' % prettyName
        lookup[row[2]] = prettyName
    html += concept.buildHTML(concept.buildConceptDict(res), 0, lookup)
    html += '</div>'
    html += """
    <script>
    $( document ).ready( function( ) {
    $( 'div.tree li' ).each( function() {
        if( $( this ).children( 'ul' ).length > 0 ) {
            $( this ).addClass( 'parent' );
        }
    });

    $( 'div.tree li.parent > a' ).click( function( ) {
        $( this ).parent().toggleClass( 'active' );
        $( this ).parent().children( 'ul' ).slideToggle( 'fast' );
    });

    $( '#all' ).click( function() {
        $( 'div.tree li' ).each( function() {
            $( this ).toggleClass( 'active' );
            $( this ).children( 'ul' ).slideToggle( 'fast' );
        });
    });
});
</script>
    """
    html += "\n"

    return html


def doListGovHoldings(form, config):
    html = ''

    query = cswaDB.getDisplayName(config, form.get('agency'))
    if query is None:
        return '<h3 class="error">Please Select An Agency.'
    else:
        query = query[0]
    hostname = config.get('connect', 'hostname')
    institution = config.get('info', 'institution')
    protocol = 'https'
    port = ''
    link = protocol + '://' + hostname + port + '/collectionspace/ui/'+institution+'/html/place.html?csid='
    sites = cswaDB.getSitesByOwner(config, form.get('agency'))
    html += '<table width="100%">'
    html += '<tr><td class="subheader" colspan="4">%s</td></tr>' % query
    html += '''<tbody align="center" width=75 style="font-weight:bold">
        <tr><td>Site</td><td>Ownership Note</td><td>Place Note</td></tr></tbody>'''
    for site in sites:
        html += "<tr>"
        for field in site:
            if not field:
                field = ''
        html += '<td align="left"><a href="' + link + str(cswaDB.getCSID('placeName',site[0], config)[0]) + '&vocab=place">' + site[0] + '</td>'
        html += '<td align="left">' + (site[2] or '') + "</td>"
        html += '<td align="left">' + (site[3] or '') + "</td>"
        html += '</tr>'
    html += "</table>"
    html += '<h4> %s sites listed.</h4>' % len(sites)

    return html


def writeCommanderFile(location, printerDir, dataType, filenameinfo, data, config):
    # slugify the location
    slug = re.sub('[^\w-]+', '_', location).strip().lower()
    barcodeFile = config.get('barcodeprint', 'cmdrfmtstring') % (
        dataType, printerDir, slug,
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"), filenameinfo)

    newName = cswaSMBclient.uploadCmdrWatch(barcodeFile, dataType, data, config)

    return newName


def doUploadUpdateLocs(data, line, id2ref, form, config):
    html = ''

    updateItems = {'crate': '', 'objectNumber': ''}
    if data[0] == "C":
        #Ex: "C","A1234567","07/22/2013 15:54","8-4216","Asian Archaeology Storage Box 0013","Kroeber, 20A, AA  1,  5"
        updateItems['handlerRefName'] = id2ref[data[1]]
        updateItems['locationDate'] = datetime.datetime.strptime(data[2], '%m/%d/%Y %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ")
        updateItems['objectNumber'] = data[3]
        updateItems['crate'] = data[4]
        updateItems['locationRefname'] = cswaDB.getrefname('locations_common', data[5], config)
        updateItems['objectCsid'] = cswaDB.getCSID("objectnumber", data[3], config)[0]
        updateItems['reason'] = form.get('reason')
    elif data[0] == "M":
        #Ex: "M","A1234567","8-4216","Kroeber, 20A, AA  1,  1","07/22/2013 15:54"
        updateItems['handlerRefName'] = id2ref[data[1]]
        updateItems['objectNumber'] = data[2]
        updateItems['locationRefname'] = cswaDB.getrefname('locations_common', data[3], config)
        updateItems['objectCsid'] = cswaDB.getCSID("objectnumber", data[2], config)[0]
        updateItems['locationDate'] = datetime.datetime.strptime(data[4], '%m/%d/%Y %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ")
        updateItems['reason'] = form.get('reason')
    elif data[0] == "R":
        #Ex: "R","A1234567","07/11/2013 17:29","Asian Archaeology Storage Box 0007","Kroeber, 20A, AA  1,  1"
        updateItems['handlerRefName'] = id2ref[data[1]]
        updateItems['locationDate'] = datetime.datetime.strptime(data[2], '%m/%d/%Y %H:%M').strftime("%Y-%m-%dT%H:%M:%SZ")
        updateItems['crate'] = data[3]
        #updateItems['locationRefname'], updateItems['objectCsid'] = cswaDB.getCSID('locations_common', data[4], config)
        updateItems['locationRefname'] = cswaDB.getrefname('locations_common', data[4], config)
        updateItems['objectCsid'] = cswaDB.getCSIDs('crateName', data[3], config)
        updateItems['reason'] = form.get('reason')
    else:
        raise Exception("<span style='color:red'>Error encountered in malformed line '%s':\nMove codes are M, C, or R!</span>" % line)

    updateItems[
        'subjectCsid'] = '' # cells[3] is actually the csid of the movement record for the current location; the updated value gets inserted later
    updateItems['inventoryNote'] = ''
    # if reason is a refname (e.g. bampfa), extract just the displayname
    reason = form.get('reason')
    reason = re.sub(r"^urn:.*'(.*)'", r'\1', reason)
    updateItems['computedSummary'] = updateItems['locationDate'][0:10] + (' (%s)' % reason)

    #html += updateItems
    numUpdated = 0
    try:
        if not isinstance(updateItems['objectCsid'], str):
            objectCsid = updateItems['objectCsid']
            for csid in objectCsid:
                updateItems['objectNumber'] = cswaDB.getCSIDDetail(config, csid[0], 'objNumber')
                updateItems['objectCsid'] = csid[0]
                updateLocations(updateItems, config)
                numUpdated += 1
                msg = 'Update successful'
                html += ('<tr>' + (3 * '<td class="ncell">%s</td>') + '</tr>\n') % (makeObjectLink(config, csid, updateItems['objectNumber']), updateItems['crate'], msg)
        else:
            updateLocations(updateItems, config)
            numUpdated += 1
            msg = 'Update successful'
            html += ('<tr>' + (3 * '<td class="ncell">%s</td>') + '</tr>\n') % (makeObjectLink(config, updateItems['objectCsid'], updateItems['objectNumber']), updateItems['inventoryNote'], msg)
    except:
        raise
        #raise Exception('<span class="error">Problem updating line %s </span>' % line)
        #msg = 'Problem updating line %s' % line
        #html += ('<tr>' + (3 * '<td class="ncell">%s</td>') + '</tr>\n') % (
        #    updateItems['objectNumber'], updateItems['inventoryNote'], msg)
    return numUpdated,html


def formatInfoReviewForm(form):
    fieldSet = form.get("fieldset")

    if fieldSet == 'namedesc':
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text"  size="60" name="onm.user"></td>
</tr><tr><th>Brief Description</th><td class="zcell"><textarea cols="78" rows="7" name="bdx.user"></textarea></td>
</tr>"""
    elif fieldSet == 'registration':
        altnumtypes, selected = cswaConstants.getAltNumTypes(form, 'user','')
        objstatuses, selected = cswaConstants.getObjectStatuses(form, 'user', '')
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text"  size="60" name="onm.user"></td>
</tr><tr><th>Alternate Number</th><td class="zcell"><input class="xspan" type="text" size="60" name="anm.user"></td>
</tr><tr><th>Alternate Number Types</th><td class="zcell">%s</td>
</tr><tr><th>Field Collector (person)</th><td class="zcell"><input class="xspan" type="text" size="60" name="cl.user"></td>
</tr><tr><th>Object Status</th><td class="zcell">%s</td>
</tr>""" % (altnumtypes, objstatuses)
    elif fieldSet == 'keyinfo':
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text"  size="60" name="onm.user"></td>
</tr><tr><th>Count</th><td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.user"></td>
</tr><tr><th>Field Collection Place</th><td class="zcell"><input class="xspan" type="text" size="60" name="cp.user"></td>
</tr><tr><th>Cultural Group</th><td class="zcell"><input class="xspan" type="text" size="60" name="cg.user"></td>
</tr><tr><th>Ethnographic File Code</th><td class="zcell"><input class="xspan" type="text" size="60" name="fc.user"></td>
</tr>"""
    elif fieldSet == 'hsrinfo':
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text" size="60" name="onm.user"></td>
</tr><tr><th>Count</th><td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.user"></td>
</tr><tr><th>Count Note</th><td class="zcell"><input class="xspan" type="text" size="25" name="ctn.user"></td>
</tr><tr><th>Field Collection Place</th><td class="zcell"><input class="xspan" type="text" size="50" name="cp.user"></td>
</tr><tr><th>Brief Description</th><td class="zcell"><textarea cols="60" rows="4" name="bdx.user"></textarea></td>
</tr>"""
    elif fieldSet == 'objtypecm':
        objtypes, selected = cswaConstants.getObjType(form, 'user', '')
        collmans, selected = cswaConstants.getCollMan(form, 'user', '')
        legacydepartments, selected = cswaConstants.getLegacyDepts(form, 'user', '')
        objstatuses, selected = cswaConstants.getObjectStatuses(form, 'user', '')
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text" size="60" name="onm.user"></td>
</tr><tr><th>Count</th><td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.user"></td>
</tr><tr><th>Object Type</th><td class="zcell">%s</td>
</tr><tr><th>Collection Manager</th><td class="zcell">%s</td>
</tr><tr><th>Field Collection Place</th><td><input class="xspan" type="text" size="60" name="cp.user"></td>
</tr><tr><th>Legacy Department</th><td class="zcell">%s</td>
</tr><tr><th>Object Status</th><td class="zcell">%s</td>
</tr>""" % (objtypes, collmans, legacydepartments, objstatuses)
    elif fieldSet == 'collection':
        return """<tr><th>Object name</th><td class="objname"><input class="objname" type="text" size="60" name="onm.user"></td>
</tr><tr><th>Collection</th><td><input class="xspan" type="text" size="60" name="cn.user"></td>
</tr>"""
    elif fieldSet == 'placeanddate':
        return """<tr><th>Object name</th>
        <td class="objname"><input class="objname" type="text" size="60" name="onm.user"></td>
</tr>
<tr><th>FCP verbatim</th>
<td><input class="xspan" type="text" size="60" name="vfcp.user"></td>
</tr>"<tr><th>Collection Date</th>
<td><input class="xspan" type="text" size="60" name="dcol.user"></td>
</tr>"""
    elif fieldSet == 'dates':
        return """<tr>
<tr><th>Production date</th><td><input class="xspan" type="text" size="40" name="dprd.user"></td></tr>
<tr><th>Collection date</th><td><input class="xspan" type="text" size="40" name="dcol.user"></td></tr>
<tr><th>Date depicted</th><td><input class="xspan" type="text" size="40" name="ddep.user"></td></tr>
<tr><th>Brief description</th><td class="zcell"><textarea cols="78" rows="5" name="bdx.user"></textarea></td></tr>
</tr>"""
    elif fieldSet == 'places':
        return """<tr>
<tr><th>FCP Verbatim</th><td><input class="xspan" type="text" size="40" name="vfcp.user"></td></tr>
<tr><th>Field collection place</th><td><input class="xspan" type="text" size="40" name="cp.user"></td></tr>
<tr><th>Production place</th><td><input class="xspan" type="text" size="40" name="pp.user"></td></tr>
<tr><th>Place depicted</th><td><input class="xspan" type="text" size="40" name="pd.user"></td></tr>
</tr>"""
    elif fieldSet == 'mattax':
        return """<tr>
<tr><th>Material</th><td><input class="xspan" type="text" size="40" name="ma.user"></td></tr>
<tr><th>Taxon</th><td><input class="xspan" type="text" size="40" name="ta.user"></td></tr>
<tr><th>Brief description</th><td class="zcell"><textarea cols="78" rows="5" name="bdx.user"></textarea></td></tr>
</tr>"""
    elif fieldSet == 'fullmonty':
        collmans, selected = cswaConstants.getCollMan(form, 'user', '')
        objstatuses, selected = cswaConstants.getObjectStatuses(form, 'user', '')
        objecttypes, selected = cswaConstants.getObjType(form, 'user', '')
        altnumtypes, selected = cswaConstants.getAltNumTypes(form, 'user', '')
        legacydepartments, selected = cswaConstants.getLegacyDepts(form, 'user', '')
        return """
<table>

<tr class="monty">

<td>Object Name<br/>
<input type="hidden" name="oox.user">
<input type="hidden" name="csid.user">
<input class="xspan" type="text" name="onm.user"></td>
</td>
</tr>

<tr class="monty">

<td>Count and Count Note<br/>
<input class="xspan" type="text" size="10" name="ocn.user">
<input class="xspan" type="text" size="20" name="ctn.user"></td>
</td>

<td>Cultural Group<br/>
<input class="xspan" type="text" size="45" name="cg.user"></td>

<td>Ethnographic File Code<br/>
<input class="xspan" type="text" size="45" name="fc.user"></td></td>

</tr>

<tr class="monty">

<td>Alt Num<br/>
<input class="xspan" type="text" size="45" name="anm.user"></td>

<td>Alt Num Type<br/>
""" + altnumtypes + """</td>

<td>Field Collector<br/>
<input class="xspan" type="text" size="45" name="cl.user"></td>

</tr>

<tr class="monty">

<td>Object type<br/>
""" + objecttypes + """</td>

<td>Production person<br/>
<input class="xspan" type="text" size="45" name="pe.user"></td>

<td>Object Status<br/>
""" + objstatuses + """</td>

</tr>

<tr class="monty">

<td>Date collected<br/>
<input class="xspan" type="text" size="45" name="dcol.user"></td>

<td>Production date<br/>
<input class="xspan" type="text" size="45" name="dprd.user"></td>

<td>Date depicted<br/>
<input class="xspan" type="text" size="45" name="ddep.user"></td>

</tr>

<tr class="monty">

<td>Materials<br/>
<input class="xspan" type="text" size="45" name="ma.user"></td>

<td>Taxon<br/>
<input class="xspan" type="text" size="45" name="ta.user"></td>

<td>Verbatim field collection place<br/>
<input class="xspan" type="text" size="45" name="vfcp.user"></td>

</tr>

<tr class="monty">

<td>Field collection place<br/>
<input class="xspan" type="text" size="45" name="cp.user"></td>

<td>Production Place<br/>
<input class="xspan" type="text" size="45" name="pp.user"></td>

<td>Place depicted<br/>
<input class="xspan" type="text" size="45" name="pd.user"></td>

</tr>

<tr>

<td>Collection Manager<br/>
""" + collmans + """</td>

<td colspan="2">Legacy Department<br/>
""" + legacydepartments + """</td>
</tr>


<tr>
<td colspan="10">Brief Description<br/>
<textarea cols="130" rows="5" name="bdx.user"></textarea>
</td>
</tr>

</table>
"""