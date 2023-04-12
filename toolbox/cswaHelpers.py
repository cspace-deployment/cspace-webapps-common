import sys, time, os
import toolbox.cswaConstants as cswaConstants
from django.conf import settings

from common import appconfig
from common.cspace import getConfig
from common.utils import devicetype

def basicSetup(form, webappconfig):
    parms = [webappconfig.get('info', 'institution')]
    tool = form.get('tool')
    for parm in 'updatetype updateactionlabel'.split(' '):
        try:
            parms.append(webappconfig.get(tool, parm))
        except:
            parms.append('')
    return parms


# get the common parameters
def configure_common_tools(context, request, action, webappconfig):
    context['serverlabel'] = webappconfig.get('info', 'serverlabel')
    context['serverlabelcolor'] = webappconfig.get('info', 'serverlabelcolor')
    context['institution'] = webappconfig.get('info', 'institution')
    context['apptitle'] = webappconfig.get(action, 'apptitle')
    context['version'] = appconfig.getversion()
    context['device'] = devicetype(request)
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    context['labels'] = 'name file'.split(' ')
    try:
        alert_config = getConfig(os.path.join(settings.BASE_DIR, 'config'), 'alert')
        context['ALERT'] = alert_config.get('alert', 'ALERT')
        context['MESSAGE'] = alert_config.get('alert', 'MESSAGE')
    except:
        context['ALERT'] = ''
    return context


def makeObjectLink(config, csid, objectnumber):
    hostname = config.get('connect', 'hostname')
    institution = config.get('info', 'institution')
    port = ''
    protocol = 'https'
    link = protocol + '://' + hostname + port + '/cspace/' + institution + '/record/all/%s' % csid
    return """<a target="cspace" href="%s">%s</a>""" % (link, objectnumber)


def handleTimeout(source, form):
    html = '<h3 class="error">Time limit exceeded! The problem has been logged and will be examined. Feel free to try again though!</h3>'
    sys.stderr.write('TIMEOUT::' + source + '::location::' + str(form.get("lo.location1")) + '::')
    return html


def validateParameters(form, config):
    html = ''
    valid = True

    if form.get('handlerRefName') == 'None':
        html += '<h3 class="error">Please select a handler before searching.</h3>'
        valid = False

    # if not str(form.get('num2ret')).isdigit():
    #    html += '<h3 class="error"><i>number to retrieve</i> must be a number, please!</h3>'
    #    valid = False

    if form.get('reason') == 'None':
        html += '<h3 class="error">Please select a reason before searching.</h3>'
        valid = False

    if form.get('action') == 'barcodeprint':
        if form.get('printer') == 'None':
            html += '<h3 class="error">Please select a printer before trying to print(labels.</h3>'
            valid = False

    # prohibitedLocations = cswaConstants.getProhibitedLocations(config, request)
    # if form.get("lo.location1"):
    #    loc = form.get("lo.location1")
    #    if loc in prohibitedLocations:
    #        html += '<h3 class="error">Location "%s" is unavailable to this webapp. Please contact registration staff for details.</h3>' % form.get(
    #            "lo.location1")
    #        valid = False


    # if form.get("lo.location2"):
    #    loc = form.get("lo.location2")
    #    if loc in prohibitedLocations:
    #        html += '<h3 class="error">Location "%s" is unavailable to this webapp. Please contact registration staff for details.</h3>' % form.get(
    #            "lo.location2")
    #        valid = False

    return valid, html


def getTableFooter(config, displaytype, updateType, msg):
    html = ''
    button = config.get(updateType, 'updateactionlabel')

    html += """<table width="100%"><tr><td align="center" colspan="3"></tr>"""
    if displaytype == 'error':
        html += """<tr><td align="center"><span style="color:red;"><b>%s</b></span></td></tr>""" % msg
    elif displaytype == 'list':
        html += """<tr><td align="center">"""
        button = 'Enumerate Objects'
        html += """<input type="submit" class="save" value="%s" name="action"></td>""" % button
        if updateType == "packinglist":
            html += """<td><input type="submit" class="save" value="%s" name="action"></td>""" % 'Download as CSV'
        else:
            html += "<td></td>"
        html += "</tr>"
    else:
        html += """<tr><td align="center">"""
        html += """<input type="submit" class="save" value="%s" name="action"></td>""" % button
        if updateType == "packinglist":
            html += """<td><input type="submit" class="save" value="%s" name="action"></td>""" % 'Download as CSV'
        if updateType == "barcodeprint":
            html += """<td><input type="submit" class="save" value="%s" name="action"></td>""" % 'Create Labels for Locations Only'
        else:
            html += "<td></td>"
        html += "</tr>"
    html += "</table>"

    return html


def relationsPayload(f):
    payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="relations">
  <ns2:relations_common xmlns:ns2="http://collectionspace.org/services/relation" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <relationshipType>affects</relationshipType>
    <objectCsid>%s</objectCsid>
    <objectDocumentType>%s</objectDocumentType>
    <subjectCsid>%s</subjectCsid>
    <subjectDocumentType>%s</subjectDocumentType>
  </ns2:relations_common>
</document>
"""
    payload = payload % (f['objectCsid'], f['objectDocumentType'], f['subjectCsid'], f['subjectDocumentType'])
    return payload


def lmiPayload(f, institution):
    if institution == 'bampfa':
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="movements">
<ns2:movements_common xmlns:ns2="http://collectionspace.org/services/movement" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<reasonForMove>%s</reasonForMove>
<currentLocation>%s</currentLocation>
<locationDate>%s</locationDate>
<movementNote>%s</movementNote>
<movementContact>%s</movementContact>
</ns2:movements_common>
<ns2:movements_bampfa xmlns:ns2="http://collectionspace.org/services/movement/domain/anthropology" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<computedSummary>%s</computedSummary>
<crate>%s</crate>
</ns2:movements_bampfa>
</document>
"""

        payload = payload % (
            f['reason'], f['locationRefname'], f['locationDate'], f['inventoryNote'], f['handlerRefName'],
            f['computedSummary'], f['crate'])

    else:
        payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="movements">
<ns2:movements_common xmlns:ns2="http://collectionspace.org/services/movement" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<reasonForMove>%s</reasonForMove>
<currentLocation>%s</currentLocation>
<currentLocationFitness>suitable</currentLocationFitness>
<locationDate>%s</locationDate>
<movementNote>%s</movementNote>
</ns2:movements_common>
<ns2:movements_anthropology xmlns:ns2="http://collectionspace.org/services/movement/domain/anthropology" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<computedSummary>%s</computedSummary>
<crate>%s</crate>
<locationHandlers>
<locationHandler>%s</locationHandler>
</locationHandlers>
</ns2:movements_anthropology>
</document>
"""
        payload = payload % (
            f['reason'], f['locationRefname'], f['locationDate'], f['inventoryNote'], f['computedSummary'], f['crate'],
            f['handlerRefName'])

    return payload


def getints(var, form):
    value = ''
    try:
        value = form.get(var)
        value = int(value)
        return value, ''
    except:
        return 'x', 'invalid value for %s: %s' % (var.replace('create.', ''), value)


def checkObject(places, objectInfo):
    if places == []:
        return True
    elif objectInfo[6] is None:
        return False
    elif objectInfo[6] in places:
        return True
    else:
        return False


def countStuff(statistics, counts, data, totalobjects):
    for s in statistics.keys():
        x = counts[s]
        if statistics[s] == 'totalobjects':
            x[totalobjects] += 1
        elif statistics[s] == 'genus':
            parts = data[1].split(' ')
            x[parts[0]] += 1
        elif statistics[s] == 'species':
            parts = data[1].split(' ex ')
            parts = parts[0].split(' var. ')
            x[parts[0]] += 1
        else:
            x[data[statistics[s]]] += 1


def setFilters(form):
    # yes, I know, it does look a bit odd...
    rare = []
    if form.get('rare'):    rare.append('true')
    if form.get('notrare'): rare.append('false')
    dead = []
    qualifier = []
    if 'dora' in form:
        dora = form.get('dora')
        if dora == 'dead':
            dead.append('true')
            qualifier.append('dead')
        elif dora == 'alive':
            dead.append('false')
            qualifier.append('alive')

    qualifier = ' or '.join(qualifier)

    return dead, rare, qualifier


def checkMembership(item, qlist):
    if item in qlist or qlist == []:
        return True
    else:
        return False


def viewLog(form, config):
    html = ''
    num2ret = int(form.get('num2ret')) if str(form.get('num2ret')).isdigit() else 100

    html += '<table>\n'
    html += ('<tr>' + (4 * '<th class="ncell">%s</td>') + '</tr>\n') % (
        'locationDate', 'objectNumber', 'objectStatus', 'handler')
    try:
        auditFile = config.get('files', 'auditfile')
        file_handle = open(auditFile)
        file_size = file_handle.tell()
        file_handle.seek(max(file_size - 9 * 1024, 0))

        lastn = file_handle.read().splitlines()[-num2ret:]
        for i in lastn:
            i = i.replace('urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name', '')
            line = ''
            if i[0] == '#': continue
            for l in [i.split('\t')[x] for x in [0, 1, 2, 5]]: line += ('<td>%s</td>' % l)
            # for l in i.split('\t') : line += ('<td>%s</td>' % l)
            html += '<tr>' + line + '</tr>'

    except:
        html += '<tr><td colspan="4">failed. sorry.</td></tr>'

    html += '</table>'


def IsAlreadyPreferred(txt, elements):
    if elements == []: return False
    if type(elements) == type([]):
        a = txt.replace('\r','').replace('\n','')
        try:
            b = elements[0].text.replace('\r','').replace('\n','')
        except:
            b = ''
        if a == b:
            # html += "    found,skipping: ",txt
            return True
        return False
    # if we were passed in a single (non-array) Element, just check it..
    if txt == str(elements.text):
        # html += "    found,skipping: ",txt
        return True
    return False


def alreadyExists(txt, elements):
    if elements == []: return False
    if type(elements) == type([]):
        for e in elements:
            a = txt.replace('\r','').replace('\n','')
            try:
                b = e.text.replace('\r','').replace('\n','')
            except:
                b = ''
            if a == b:
                # html += "    found,skipping: ",txt
                return True
        return False
    # if we were passed in a single (non-array) Element, just check it..
    if txt == str(elements.text):
        # html += "    found,skipping: ",txt
        return True
    return False


def starthtml(form, updateType, config):
    schemacolor1 = config.get('info', 'schemacolor1')
    institution = config.get('info', 'institution')

    msg = ''

    button = '''<input id="actionbutton" class="save" type="submit" value="Search" name="action">'''

    appOptions = '''
    <a target="help" href="%s">Help</a>
    ''' % ('https://webapps.cspace.berkeley.edu/webappmanual/%s-webappmanual.html' % institution)

    # temporary, until the other groupings and sortings work...
    groupbyelement = '''
          <th><span class="cell">group by: </span></th>
          <th><span class="cell">none </span><input type="radio" name="groupby" value="none">
          <span class="cell">location </span><input type="radio" name="groupby" value="location"></th>
          '''

    groupby = str(form.get("groupby")) if form.get("groupby") else 'location'
    groupbyelement = groupbyelement.replace(('value="%s"' % groupby), ('checked value="%s"' % groupby))

    reporttypeelement = '''
          <th><span class="cell">report type:</span></th>
          <th>
          <select class="cell" name="reporttype">
          <option value="standard">standard</option>
          <option value="details">location details</option>
          </select>
          </th>
          '''
    reporttype = str(form.get("reporttype")) if form.get("reporttype") else 'standard'
    reporttypeelement = reporttypeelement.replace(('value="%s"' % reporttype), ('selected value="%s"' % reporttype))

    deadoralive = '''
      <th><span class="cell">filters: </span></th>
      <th><span class="cell">rare </span>
	  <input id="rare" class="cell" type="checkbox" name="rare" value="rare" class="xspan">
          <span class="cell">not rare </span>
	  <input id="notrare" class="cell" type="checkbox" name="notrare" value="notrare" class="xspan">
          ||
	  <span class="cell">alive </span>
	  <input id="alive" class="cell" type="radio" name="dora" value="alive" class="xspan">
	  <span class="cell">dead </span>
	  <input id="dead" class="cell" type="radio" name="dora" value="dead" class="xspan"></th>'''

    for v in ['rare', 'notrare']:
        if form.get(v):
            deadoralive = deadoralive.replace('value="%s"' % v, 'checked value="%s"' % v)
        else:
            deadoralive = deadoralive.replace('checked value="%s"' % v, 'value="%s"' % v)
    if 'dora' in form:
        deadoralive = deadoralive.replace('value="%s"' % form['dora'], 'checked value="%s"' % form['dora'])
    else:
        deadoralive = deadoralive.replace('value="%s"' % 'alive', 'checked value="%s"' % 'alive')

    location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
    location2 = str(form.get("lo.location2")) if form.get("lo.location2") else ''
    otherfields = '''
    <tr><th><span class="cell">start location:</span></th>
    <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
    <th><span class="cell">end location:</span></th>
    <th><input id="lo.location2" class="cell" type="text" size="40" name="lo.location2" value="''' + location2 + '''" class="xspan"></th></tr>
    '''

    if updateType == 'keyinfo':
        location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
        location2 = str(form.get("lo.location2")) if form.get("lo.location2") else ''
        fieldset, selected = cswaConstants.getFieldset(form, institution)

        otherfields = '''
        <tr><th><span class="cell">start location:</span></th>
        <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
        <th><span class="cell">end location:</span></th>
        <th><input id="lo.location2" class="cell" type="text" size="40" name="lo.location2" value="''' + location2 + '''" class="xspan"></th>
        <th><th><span class="cell">set:</span></th><th>''' + fieldset + '''</th></tr>
        '''
        otherfields += '''
        <tr></tr>'''

    elif updateType == 'objinfo':
        objno1 = str(form.get("ob.objno1")) if form.get("ob.objno1") else ''
        objno2 = str(form.get("ob.objno2")) if form.get("ob.objno2") else ''
        fieldset, selected = cswaConstants.getFieldset(form, institution)

        otherfields = '''
        <tr><th><span class="cell">start object no:</span></th>
        <th><input id="ob.objno1" class="cell" type="text" size="32" name="ob.objno1" value="''' + objno1 + '''" class="xspan"></th>
        <th><span class="cell">end object no:</span></th>
        <th><input id="ob.objno2" class="cell" type="text" size="32" name="ob.objno2" value="''' + objno2 + '''" class="xspan"></th>
        <th><th><span class="cell">set:</span></th><th>''' + fieldset + '''</th></tr>
        '''
        otherfields += '''
        <tr></tr>'''

    elif updateType == 'bulkedit':
        fieldset, selected = cswaConstants.getFieldset(form, institution)

        location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
        location2 = str(form.get("lo.location2")) if form.get("lo.location2") else ''

        grpinfo = str(form.get("gr.group")) if form.get("gr.group") else ''
        objno1 = str(form.get("ob.objno1")) if form.get("ob.objno1") else ''
        objno2 = str(form.get("ob.objno2")) if form.get("ob.objno2") else ''

        otherfields = '''
        <tr>
        <th><span class="cell">start location:</span></th>
        <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
        <th><span class="cell">end location:</span></th>
        <th><input id="lo.location2" class="cell" type="text" size="40" name="lo.location2" value="''' + location2 + '''" class="xspan"></th>
        <th><th><span class="cell">set:</span></th><th>''' + fieldset + '''</th>
        </tr>

        <tr>
        <th><span class="cell">first museum number:</span></th>
        <th><input id="ob.objno1" class="cell" type="text" size="40" name="ob.objno1" value="''' + objno1 + '''" class="xspan"></th>
        <th><span class="cell">last museum number:</span></th>
        <th><input id="ob.objno2" class="cell" type="text" size="40" name="ob.objno2" value="''' + objno2 + '''" class="xspan">
        </tr>
        <tr>
        <th><span class="cell">group:</span></th>
        <th><input id="gr.group" class="cell" type="text" size="40" name="gr.group" value="''' + grpinfo + '''" class="xspan"></th>
        <th colspan="4"><i>NB: object number range supersedes location range, if entered;</i><br/>
        <i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group identifier supersedes both, if entered.</i></th>
        </tr>'''

    elif updateType == 'moveobject':
        objno1 = str(form.get("ob.objno1")) if form.get("ob.objno1") else ''
        objno2 = str(form.get("ob.objno2")) if form.get("ob.objno2") else ''
        crate = str(form.get("lo.crate")) if form.get("lo.crate") else ''
        handlers, selected = cswaConstants.getHandlers(form, institution)
        reasons, selected = cswaConstants.getReasons(form, institution)

        otherfields = '''
        <tr><th><span class="cell">start object no:</span></th>
        <th><input id="ob.objno1" class="cell" type="text" size="40" name="ob.objno1" value="''' + objno1 + '''" class="xspan"></th>
        <th><span class="cell">end object no:</span></th>
        <th><input id="ob.objno2" class="cell" type="text" size="40" name="ob.objno2" value="''' + objno2 + '''" class="xspan"></th></tr>
        '''
        otherfields += '''
        <tr><th><span class="cell">destination:</span></th>
        <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
        <th><span class="cell">reason:</span></th><th>''' + reasons + '''</th>
        <tr><th><span class="cell">crate:</span></th>
        <th><input id="lo.crate" class="cell" type="text" size="40" name="lo.crate" value="''' + crate + '''" class="xspan"></th>
        <th><span class="cell">handler:</span></th><th>''' + handlers + '''</th></tr>
        '''

    elif updateType == 'grpinfo':
        grpinfo = str(form.get("gr.group")) if form.get("gr.group") else ''
        fieldset, selected = cswaConstants.getFieldset(form, institution)

        otherfields = '''
        <tr><th><span class="cell">group:</span></th>
        <th><input id="gr.group" class="cell" type="text" size="40" name="gr.group" value="''' + grpinfo + '''" class="xspan"></th>
        <th><th><span class="cell">set:</span></th><th>''' + fieldset + '''</th></tr>'''
        otherfields += '''
        <tr></tr>'''

    elif updateType == 'createobjects':

        year = str(form.get("create.year")) if form.get("create.year") else ''
        accession = str(form.get("create.accession")) if form.get("create.accession") else ''
        sequence = str(form.get("create.sequence")) if form.get("create.sequence") else ''
        count = str(form.get("create.count")) if form.get("create.count") else ''

        otherfields = '''
            <tr><th><span class="cell">year:</span></th>
            <th><input id="create.year" class="cell" type="text" size="40" name="create.year" value="''' + year + '''" class="xspan"></th></tr>'''

        otherfields += '''
            <tr><th><span class="cell">accession:</span></th>
            <th><input id="create.accession" class="cell" type="text" size="40" name="create.accession" value="''' + accession + '''" class="xspan"></th></tr>'''

        otherfields += '''
            <tr><th><span class="cell">sequence:</span></th>
            <th><input id="create.sequence" class="cell" type="text" size="40" name="create.sequence" value="''' + sequence + '''" class="xspan"></th></tr>'''

        otherfields += '''
            <tr><th><span class="cell">count:</span></th>
            <th><input id="create.count" class="cell" type="text" size="40" name="create.count" value="''' + count + '''" class="xspan"></th></tr>'''

    elif updateType == 'movecrate':
        crate = str(form.get("lo.crate")) if form.get("lo.crate") else ''
        otherfields = '''
        <tr><th><span class="cell">from:</span></th>
        <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
        <th><span class="cell">to:</span></th>
        <th><input id="lo.location2" class="cell" type="text" size="40" name="lo.location2" value="''' + location2 + '''" class="xspan"></th></tr>
        <tr><th><span class="cell">crate:</span></th>
        <th><input id="lo.crate" class="cell" type="text" size="40" name="lo.crate" value="''' + crate + '''" class="xspan"></th></tr>
    '''

        handlers, selected = cswaConstants.getHandlers(form, institution)
        reasons, selected = cswaConstants.getReasons(form, institution)
        otherfields += '''
          <tr><th><span class="cell">reason:</span></th><th>''' + reasons + '''</th>
          <th><span class="cell">handler:</span></th><th>''' + handlers + '''</th></tr>'''


    elif updateType == 'grpmove':
        grpinfo = str(form.get("gr.group")) if form.get("gr.group") else ''
        location = str(form.get("lo.location")) if form.get("lo.location") else ''

        handlers, selected = cswaConstants.getHandlers(form, institution)
        reasons, selected = cswaConstants.getReasons(form, institution)

        otherfields = '''
            <tr><th><span class="cell">group:</span></th>
            <th><input id="gr.group" class="cell" type="text" size="40" name="gr.group" value="''' + grpinfo + '''" class="xspan"></th>
            <th><span class="cell">to location:</span></th>
            <th><input id="lo.location" class="cell" type="text" size="40" name="lo.location" value="''' + location + '''" class="xspan"></th></tr>
            <tr><th><span class="cell">reason:</span></th><th>''' + reasons + '''</th>
            <th><span class="cell">contact:</span></th><th>''' + handlers + '''</th></tr>'''


    elif updateType == 'powermove':
        location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
        location2 = str(form.get("lo.location2")) if form.get("lo.location2") else ''
        crate1 = str(form.get("lo.crate1")) if form.get("lo.crate1") else ''
        crate2 = str(form.get("lo.crate2")) if form.get("lo.crate2") else ''
        otherfields = '''
        <tr><th><span class="cell">from location:</span></th>
        <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
        <th><span class="cell">to location:</span></th>
        <th><input id="lo.location2" class="cell" type="text" size="40" name="lo.location2" value="''' + location2 + '''" class="xspan"></th></tr>
        <tr><th><span class="cell">crate (optional):</span></th>
        <th><input id="lo.crate1" class="cell" type="text" size="40" name="lo.crate1" value="''' + crate1 + '''" class="xspan"></th>
        <th><span class="cell">crate (optional):</span></th>
        <th><input id="lo.crate2" class="cell" type="text" size="40" name="lo.crate2" value="''' + crate2 + '''" class="xspan"></th></tr>
    '''

        handlers, selected = cswaConstants.getHandlers(form, institution)
        reasons, selected = cswaConstants.getReasons(form, institution)
        otherfields += '''
          <tr><th><span class="cell">reason:</span></th><th>''' + reasons + '''</th>
          <th><span class="cell">handler:</span></th><th>''' + handlers + '''</th></tr>'''

    elif updateType == 'bedlist':
        location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
        otherfields = '''
        <tr>
            <th><span rowspan="2" class="cell">bed:</span></th>
            <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
            <th>
                <table><tr>''' + groupbyelement + '''</tr>
                 <tr>''' + deadoralive + '''</tr>
                 <tr>''' + reporttypeelement + '''</tr>
                </table>
            </th>
        </tr>
        </tr>'''

    elif updateType == 'locreport':
        taxName = str(form.get('ut.taxon')) if form.get('ut.taxon') else ''
        otherfields = '''
        <tr><th><span class="cell">taxonomic name:</span></th>
        <th><input id="ut.taxon" class="cell" type="text" size="40" name="ut.taxon" value="''' + taxName + '''" class="xspan"></th>
        ''' + deadoralive + '''</tr> '''

    elif updateType == 'holdings':
        place = str(form.get('px.place')) if form.get('px.place') else ''
        otherfields = '''
        <tr><th><span class="cell">collection place:</span></th>
        <th><input id="px.place" class="cell" type="text" size="40" name="px.place" value="''' + place + '''" class="xspan"></th>
        ''' + deadoralive + '''</tr> '''

    elif updateType == 'advsearch':
        location1 = str(form.get("lo.location1")) if form.get("lo.location1") else ''
        taxName = str(form.get('ut.taxon')) if form.get('ut.taxon') else ''
        objectnumber = str(form.get('ob.objectnumber')) if form.get('ob.objectnumber') else ''
        place = str(form.get('px.place')) if form.get('px.place') else ''
        concept = str(form.get('cx.concept')) if form.get('cx.concept') else ''

        otherfields = '''
	  <tr><th><span class="cell">taxonomic name:</span></th>
	  <th><input id="ut.taxon" class="cell" type="text" size="40" name="ut.taxon" value="''' + taxName + '''" class="xspan"></th>
          ''' + groupbyelement + '''</tr>
	  <tr>
          <th><span class="cell">bed:</span></th>
	  <th><input id="lo.location1" class="cell" type="text" size="40" name="lo.location1" value="''' + location1 + '''" class="xspan"></th>
          ''' + deadoralive + '''</tr>
	  <tr><th><span class="cell">collection place:</span></th>
	  <th><input id="px.place" class="cell" type="text" size="40" name="px.place" value="''' + place + '''" class="xspan"></th>
	  </tr>
          '''

        saveForNow = '''
	  <tr><th><span class="cell">concept:</span></th>
	  <th><input id="cx.concept" class="cell" type="text" size="40" name="cx.concept" value="''' + concept + '''" class="xspan"></th></tr>'''

    elif updateType == 'search':
        objectnumber = str(form.get('ob.objectnumber')) if form.get('ob.objectnumber') else ''
        place = str(form.get('cp.place')) if form.get('cp.place') else ''
        concept = str(form.get('co.concept')) if form.get('co.concept') else ''
        otherfields += '''
	  <tr><th><span class="cell">museum number:</span></th>
	  <th><input id="ob.objectnumber" class="cell" type="text" size="40" name="ob.objectnumber" value="''' + objectnumber + '''" class="xspan"></th></tr>
	  <tr><th><span class="cell">concept:</span></th>
	  <th><input id="co.concept" class="cell" type="text" size="40" name="co.concept" value="''' + concept + '''" class="xspan"></th></tr>
	  <tr><th><span class="cell">collection place:</span></th>
	  <th><input id="cp.place" class="cell" type="text" size="40" name="cp.place" value="''' + place + '''" class="xspan"></th></tr>'''

    elif updateType == 'barcodeprint':
        printers, selected, printerlist = cswaConstants.getPrinters(form)
        grpinfo = str(form.get("gr.group")) if form.get("gr.group") else ''
        objno1 = str(form.get("ob.objno1")) if form.get("ob.objno1") else ''
        objno2 = str(form.get("ob.objno2")) if form.get("ob.objno2") else ''
        otherfields += '''
<tr><th><span class="cell">first museum number:</span></th>
<th><input id="ob.objno1" class="cell" type="text" size="40" name="ob.objno1" value="''' + objno1 + '''" class="xspan"></th>
<th><span class="cell">last museum number:</span></th>
<th><input id="ob.objno2" class="cell" type="text" size="40" name="ob.objno2" value="''' + objno2 + '''" class="xspan"></tr>
<tr><th><span class="cell">group:</span></th>
<th><input id="gr.group" class="cell" type="text" size="40" name="gr.group" value="''' + grpinfo + '''" class="xspan"></th>
<th colspan="4"><i>NB: object number range supersedes location range, if entered;</i><br/></th>
<tr><th><span class="cell">printer cluster:</span></th><th>''' + printers + '''</th>
<th colspan="4"><i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;group identifier supersedes both, if entered.</i></th>
</tr>'''

    elif updateType == 'inventory':
        handlers, selected = cswaConstants.getHandlers(form, institution)
        reasons, selected = cswaConstants.getReasons(form, institution)
        otherfields += '''
          <tr><th><span class="cell">reason:</span></th><th>''' + reasons + '''</th>
          <th><span class="cell">handler:</span></th><th>''' + handlers + '''</th></tr>'''

    elif updateType == 'packinglist' or updateType == 'packinglistbyculture':
        if institution == 'bampfa':
            pass
        else:
            place = str(form.get('cp.place')) if form.get('cp.place') else ''
            otherfields += '''
	  <tr><th><span class="cell">collection place:</span></th>
	  <th><input id="cp.place" class="cell" type="text" size="40" name="cp.place" value="''' + place + '''" class="xspan"></th>'''
            otherfields += '''
          <th><span class="cell">group by culture </span></th>
	  <th><input id="groupbyculture" class="cell" type="checkbox" name="groupbyculture" value="groupbyculture" class="xspan"></th</tr>'''
            if form.get('groupbyculture'): otherfields = otherfields.replace('value="groupbyculture"',
                                                                             'checked value="groupbyculture"')

    elif updateType == 'hierarchyviewer':

        authorities = config.get('hierarchyviewer', 'authorities').split(',')
        hierarchies, selected = cswaConstants.getHierarchies(form, authorities)
        button = '''<input id="actionbutton" class="save" type="submit" value="View Hierarchy" name="action">'''
        otherfields = '''<tr><th><span class="cell">Authority:</span></th><th>''' + hierarchies + '''</th></tr>'''

    elif updateType == 'governmentholdings':
        agencies, selected = cswaConstants.getAgencies(form)
        button = '''<input id="actionbutton" class="save" type="submit" value="View Holdings" name="action">'''
        otherfields = '''<tr><th><span class="cell">Agency:</span></th><th>''' + agencies + '''</th>'''
        otherfields += """<td><input type="submit" class="save" value="%s" name="action"></td>""" % 'Download as CSV'

    elif updateType == 'intake':

        fielddescription = cswaConstants.getIntakeFields('intake')

        button = '''
            <input id="actionbutton" class="save" type="submit" value="Start Intake" name="action">
            <input id="actionbutton" class="save" type="submit" value="View Intakes" name="action"><br/>
            '''

        otherfields = '<tr>'
        for i, box in enumerate(fielddescription):
            if i % 3 == 0:
                otherfields += "</tr><tr>"
            if box[4] == 'fixed':
                otherfields += '''
                <th><span class="cell">%s</span></th>
                <th><input id="%s" class="cell" type="hidden" size="%s" name="%s" value="%s" class="xspan">
                <b>%s</b></th>
                ''' % (box[0], box[2], box[1], box[2], box[3], box[3])
            else:
                otherfields += '''
                 <th><span class="cell">%s</span></th>
                <th><input id="%s" class="cell" type="%s" size="%s" name="%s" value="%s" class="xspan"></th>
                ''' % (box[0], box[2], box[4], box[1], box[2], box[3])
        otherfields += '</tr>'

    else:
        otherfields = '''
          <th><span class="cell">problem:</span></th>
          <th>internal error: updateType not specified</th></tr>
          <tr><th/><th/><th/><th/></tr>'''

    staticurl = settings.STATIC_URL
    return cswaConstants.getStyle(schemacolor1) + '''
    <div style="width:150px;" id="appstatus"><img height="60px" src="''' + staticurl + '''cspace_django_site/images/timer-animated.gif" alt="Working..."><div style="float: right;margin-top: 20px; color: gray;" class="objno">Working...</div></div>
    <table width="100%">
        <tr>
        <th>
        <table>
	  ''' + otherfields + '''
        </table>
        </th>
        <th style="width:80px;text-align:center;">''' + button + '''</th>
        </tr>
    </table>
'''


def endhtml(form, config, elapsedtime):
    addenda = """
    $('[name="action"]').click(function () {
        $('#appstatus').css({ display: "block" });
        // $('[name="action"]').css({ "background-color": "lightgray" });
        // $('[name="action"]').prop('disabled', true);
    });
    $('#appstatus').css({ display: "none" });
    $('[name="action"]').prop('disabled', false);
});"""

    focusSnippet = '''$('input:text:first').focus();'''

    return '''
</tbody></table>
</form>
<script>
$(function () {
       $("[name^=select-]").click(function (event) {
           var selected = this.checked;
           var mySet    = $(this).attr("name");
           mySet = mySet.replace('select-','');
           // console.log(mySet);
           // Iterate each checkbox
           $("[name^=" + mySet + "]").each(function () { this.checked = selected; });
       });
    });

$(document).on('click', '#check-move', function() {
    if ($('#check-move').is(':checked')) {
        $('input[id="sel-move"]').each(function () { this.checked = true; });
    } else {
        $('input[id="sel-nomove"]').each(function () { this.checked = true; });
    }
});


$(document).ready(function () {

''' + focusSnippet + '''

$(function() {
  $('[id^="sortTable"]').map(function() {
        // console.log(this);
        $(this).tablesorter({debug: true})
     });
  });

$('[name]').map(function() {
    var elementID = $(this).attr('name');
    if (elementID.indexOf('.') == 2) {
        // console.log(elementID);
        $(this).autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: "../suggest",
                    dataType: "json",
                    data: {
                        q : request.term,
                        elementID : elementID,
                        source: 'postgres'
                    },
                    success: function(data) {
                        response(data);
                    }
                });
            },
            minLength: 2,
        });
    }
});''' + addenda + '</script>'
