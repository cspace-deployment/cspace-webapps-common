import cgi
import toolbox.cswaConstants as cswaConstants
import toolbox.cswaDB as cswaDB


def formatRow(result, form, config):
    hostname = config.get('connect', 'hostname')
    institution = config.get('info', 'institution')
    port = ''
    protocol = 'https'
    rr = result['data']
    rr = [x if x != None else '' for x in rr]

    try:
        csid = rr[8]
    except:
        csid = 'user'
    link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/cataloging.html?csid=%s' % csid

    # the link to acquisitions is for PAHMA...
    try:
        link2 = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/acquisition.html?csid=%s' % rr[24]
    except:
        link2 = ''

    if result['rowtype'] == 'subheader':
        return """<tr><td colspan="7" class="subheader">%s</td></tr>""" % result['data'][0]
    elif result['rowtype'] == 'location':
        return '''<tr><td class="objno"><a href="#" onclick="formSubmit('%s')">%s</a> <span style="color:red;">%s</span></td><td/></tr>''' % (
            result['data'][0], result['data'][0], '')
    elif result['rowtype'] == 'select':
        rr = result['data']
        boxType = result['boxtype']
        return '''<li class="xspan"><input type="checkbox" name="%s.%s" value="%s" checked> <a href="#" onclick="formSubmit('%s')">%s</a></li>''' % (
            (boxType,) + (rr[0],) * 4)
    elif result['rowtype'] == 'bedlist':
        groupby = str(form.get("groupby"))
        rare = 'Yes' if rr[8] == 'true' else 'No'
        dead = 'Yes' if rr[9] == 'true' else 'No'
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/cataloging.html?csid=%s' % rr[7]
        if groupby == 'none':
            location = '<td class="zcell">%s</td>' % rr[0]
        else:
            location = ''
        return '''<tr><td class="objno"><a target="cspace" href="%s">%s</a</td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td>%s</tr>''' % (
            link, rr[4], rr[6], rr[5], rare, dead, location)
    elif result['rowtype'] in ['locreport', 'holdings', 'advsearch']:
        rare = 'Yes' if rr[7] == 'true' else 'No'
        dead = 'Yes' if rr[8] == 'true' else 'No'
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution + '/html/cataloging.html?csid=%s' % rr[6]
        return '''<tr><td class="zcell"><a target="cspace" href="%s">%s</a></td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td><td class="zcell">%s</td></tr>''' % (
            link, rr[0], rr[1], rr[2], rr[3], rr[5], rare, dead)
    elif result['rowtype'] == 'inventory':
        if institution == 'bampfa':
            return """<tr><td class="objno"><a target="cspace" href="%s">%s</a></td><td class="objname">%s</td><td>%s</td><td class="rdo" ><input type="radio" id="sel-move" name="r.%s" value="found|%s|%s|%s|%s|%s" checked></td><td class="rdo" ><input type="radio" id="sel-nomove" name="r.%s" value="not found|%s|%s|%s|%s|%s"/></td><td class="zcell"><input class="xspan" type="text" size="65" name="n.%s"></td></tr>""" % (
                link, rr[3], rr[5], rr[16], rr[3], rr[8], rr[7], rr[6], rr[3], rr[14], rr[3], rr[8], rr[7], rr[6],
                rr[3], rr[14], rr[3])
        else:
            return """<tr><td class="objno"><a target="cspace" href="%s">%s</a></td><td class="objname">%s</td><td class="rdo" ><input type="radio" id="sel-move" name="r.%s" value="found|%s|%s|%s|%s|%s" checked></td><td class="rdo" ><input type="radio" id="sel-nomove" name="r.%s" value="not found|%s|%s|%s|%s|%s"/></td><td class="zcell"><input class="xspan" type="text" size="65" name="n.%s"></td></tr>""" % (
                link, rr[3], rr[5], rr[3], rr[8], rr[7], rr[6], rr[3], rr[14], rr[3], rr[8], rr[7], rr[6],
                rr[3], rr[14], rr[3])
    elif result['rowtype'] == 'powermove':
        if institution == 'bampfa':
            return """<tr><td class="objno"><a target="cspace" href="%s">%s</a></td><td class="objname">%s</td><td>%s</td><td class="rdo" ><input type="radio" id="sel-move" name="r.%s" value="found|%s|%s|%s|%s|%s"></td><td class="rdo" ><input type="radio" id="sel-nomove" name="r.%s" value="do not move|%s|%s|%s|%s|%s" checked/></td><td class="zcell"><input class="xspan" type="text" size="65" name="n.%s"></td></tr>""" % (
                link, rr[3], rr[5], rr[16], rr[3], rr[8], rr[7], rr[6], rr[3], rr[14], rr[3], rr[8], rr[7], rr[6],
                rr[3], rr[14], rr[3])
        return """<tr><td class="objno"><a target="cspace" href="%s">%s</a></td><td class="objname">%s</td><td class="rdo" ><input type="radio" id="sel-move" name="r.%s" value="move|%s|%s|%s|%s|%s"></td><td class="rdo" ><input type="radio" id="sel-nomove" name="r.%s" value="do not move|%s|%s|%s|%s|%s" checked/></td><td class="zcell"><input class="xspan" type="text" size="65" name="n.%s"></td></tr>""" % (
            link, rr[3], rr[5], rr[3], rr[8], rr[7], rr[6], rr[3], rr[14], rr[3], rr[8], rr[7], rr[6],
            rr[3], rr[14], rr[3])
    elif result['rowtype'] == 'moveobject':
        return """<tr><td class="rdo" ><input type="checkbox" name="r.%s" value="moved|%s|%s|%s|%s|%s" checked></td><td class="objno"><a target="cspace" href="%s">%s</a></td><td class="objname">%s</td><td class="zcell">%s</td><td class="zcell">%s</td></tr>""" % (
            rr[3], rr[8], rr[1], '', rr[3], rr[13], link, rr[3], rr[4], rr[5], rr[0])
    elif result['rowtype'] == 'keyinfo' or result['rowtype'] == 'objinfo':
        return formatInfoReviewRow(form, link, rr, link2)
    elif result['rowtype'] == 'packinglist':
        if institution == 'bampfa':
            return """
            <tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname" name="ti.%s">%s</td>
<td class="ncell" name="ar.%s">%s</td>
<td class="ncell" name="me.%s">%s</td>
<td class="ncell" name="di.%s">%s</td>
<td class="ncell" name="cl.%s">%s</td>
</tr>""" % (link, rr[1], rr[2], rr[3], rr[2], rr[4], rr[2], rr[6], rr[2], rr[7], rr[2], rr[9])

        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname" name="onm.%s">%s</td>
<td class="xspan" name="ocn.%s">%s</td>
<td class="xspan" name="cp.%s">%s</td>
<td class="xspan" name="cg.%s">%s</td>
<td class="xspan" name="fc.%s">%s</td>
</tr>""" % (link, rr[3], rr[8], rr[4], rr[8], rr[5], rr[8], rr[6], rr[8], rr[7], rr[8], rr[9])

    elif result['rowtype'] == 'packinglistbyculture':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname" name="onm.%s">%s</td>
<td class="xspan" name="ocn.%s">%s</td>
<td class="xspan">%s</td>
<td class="xspan" name="fc.%s">%s</td>
</tr>""" % (link, rr[3], rr[8], rr[4], rr[8], rr[5], rr[7], rr[8], rr[6])


def formatInfoReviewRow(form, link, rr, link2):
    fieldSet = form.get("fieldset")
    if fieldSet == 'namedesc':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input class="objname" type="text" name="onm.%s" value="%s"></td>
<td width="0"></td>
<input type="hidden" name="oox.%s" value="%s"><input type="hidden" name="csid.%s" value="%s">
<td class="zcell">
<textarea cols="78" rows="5" name="bdx.%s">%s</textarea></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], cgi.escape(rr[4], True), rr[8], cgi.escape(rr[3], True), rr[8], rr[8],
            rr[8], cgi.escape(rr[15], True))
    elif fieldSet == 'registration':
        altnumtypes, selected = cswaConstants.getAltNumTypes(form, rr[8], rr[19])
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input class="objname" type="text" name="onm.%s" value="%s"></td>
<td class="zcell">
<input type="hidden" name="oox.%s" value="%s">
<input type="hidden" name="csid.%s" value="%s">
<input class="xspan" type="text" size="13" name="anm.%s" value="%s"></td>
<td class="zcell">%s</td>
<td class="zcell"><input class="xspan" type="text" size="26" name="cl.%s" value="%s"></td>
<td class="zcell"><span style="font-size:8">%s</span></td>
<td class="zcell"><a target="cspace" href="%s">%s</a></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], cgi.escape(rr[4], True), rr[8], cgi.escape(rr[3], True), rr[8], rr[8],
            rr[8], cgi.escape(rr[18], True), altnumtypes, rr[8], cgi.escape(rr[16], True), cgi.escape(rr[17], True),
            link2, cgi.escape(rr[21], True))
    elif fieldSet == 'keyinfo':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input class="objname" type="text" name="onm.%s" value="%s"></td>
<td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.%s" value="%s"></td>
<td class="zcell">
<input type="hidden" name="oox.%s" value="%s">
<input type="hidden" name="csid.%s" value="%s">
<input class="xspan" type="text" size="26" name="cp.%s" value="%s"></td>
<td class="zcell"><input class="xspan" type="text" size="26" name="cg.%s" value="%s"></td>
<td class="zcell"><input class="xspan" type="text" size="26" name="fc.%s" value="%s"></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], cgi.escape(rr[4], True), rr[8], rr[5], rr[8], cgi.escape(rr[3], True),
            rr[8], rr[8], rr[8], cgi.escape(rr[6], True), rr[8], cgi.escape(rr[7], True), rr[8],
            cgi.escape(rr[9], True))
    elif fieldSet == 'hsrinfo':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input class="objname" type="text" name="onm.%s" value="%s"></td>
<td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.%s" value="%s"></td>
<td class="zcell">
<input type="hidden" name="oox.%s" value="%s">
<input type="hidden" name="csid.%s" value="%s">
<input class="xspan" type="text" size="20" name="ctn.%s" value="%s"></td>
<td class="zcell"><input class="xspan" type="text" size="26" name="cp.%s" value="%s"></td>
<td class="zcell"><textarea cols="78" rows="5" name="bdx.%s">%s</textarea></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], cgi.escape(rr[4], True),
            rr[8], rr[5],
            rr[8], cgi.escape(rr[3], True),
            rr[8], rr[8], rr[8], cgi.escape(rr[25], True),
            rr[8], cgi.escape(rr[6], True), rr[8],
            cgi.escape(rr[15], True))
    elif fieldSet == 'objtypecm':
        objtypes, selected = cswaConstants.getObjType(form, rr[8], rr[26])
        collmans, selected = cswaConstants.getCollMan(form, rr[8], rr[27])
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input class="objname" type="text" name="onm.%s" value="%s"></td>
<td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.%s" value="%s"></td>
<td><input type="hidden" name="oox.%s" value="%s"><input type="hidden" name="csid.%s" value="%s">%s</td>
<td>%s</td>
<td><input class="xspan" type="text" size="26" name="cp.%s" value="%s"></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], cgi.escape(rr[4], True),
            rr[8], rr[5],
            rr[8], cgi.escape(rr[3], True),
            rr[8], rr[8], objtypes, collmans,
            rr[8], cgi.escape(rr[6], True))
    elif fieldSet == 'collection':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<input type="hidden" name="clnx.%s" value="%s">
<input type="hidden" name="csid.%s" value="%s">
<td><input class="xspan" type="text" size="40" name="cln.%s" value="%s"></td>
</tr>""" % (link, cgi.escape(rr[1], True), rr[2], cgi.escape(rr[3], True), rr[2], rr[22], rr[2], rr[2], rr[2],
            cgi.escape(rr[8], True))
    elif fieldSet == 'placeanddate':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<input type="hidden" name="csid.%s" value="%s">
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<td><input class="xspan" type="text" size="40" name="vfcp.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="dcol.%s" value="%s"></td>
</tr>""" % (
        link, cgi.escape(rr[3], True), rr[8], rr[8], rr[8], cgi.escape(rr[4], True),
        rr[8], cgi.escape(rr[28], True),
        rr[8], cgi.escape(rr[29], True))
    elif fieldSet == 'dates':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<input type="hidden" name="csid.%s" value="%s">
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<td><input class="xspan" type="text" size="40" name="dprd.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="dcol.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="ddep.%s" value="%s"></td>
<td class="zcell"><textarea cols="78" rows="5" name="bdx.%s">%s</textarea></td>
</tr>""" % (
        link, cgi.escape(rr[3], True), rr[8], rr[8], rr[8], cgi.escape(rr[4], True),
        rr[8], cgi.escape(rr[32], True),
        rr[8], cgi.escape(rr[29], True),
        rr[8], cgi.escape(rr[34], True),
        rr[8], cgi.escape(rr[15], True))
    elif fieldSet == 'places':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<input type="hidden" name="csid.%s" value="%s">
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<td><input class="xspan" type="text" size="40" name="vfcp.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="cp.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="pp.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="pd.%s" value="%s"></td>
</tr>""" % (
        link, cgi.escape(rr[3], True), rr[8], rr[8], rr[8], cgi.escape(rr[4], True),
        rr[8], cgi.escape(rr[28], True),
        rr[8], cgi.escape(rr[6], True),
        rr[8], cgi.escape(rr[31], True),
        rr[8], cgi.escape(rr[35], True))
    elif fieldSet == 'mattax':
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<input type="hidden" name="csid.%s" value="%s">
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<td><input class="xspan" type="text" size="40" name="ma.%s" value="%s"></td>
<td><input class="xspan" type="text" size="40" name="ta.%s" value="%s"></td>
<td class="zcell"><textarea cols="78" rows="5" name="bdx.%s">%s</textarea></td>
</tr>""" % (link, cgi.escape(rr[3], True), rr[8], rr[8], rr[8], cgi.escape(rr[4], True),
            rr[8], cgi.escape(rr[30], True),
            rr[8], cgi.escape(rr[33], True),
            rr[8], cgi.escape(rr[15], True))
    elif fieldSet == 'fullmonty':
        collmans, selected = cswaConstants.getCollMan(form, rr[8], rr[27])
        objstatuses, selected = cswaConstants.getObjectStatuses(form, rr[8], rr[37])
        objecttypes, selected = cswaConstants.getObjType(form, rr[8], rr[26])
        altnumtypes, selected = cswaConstants.getAltNumTypes(form, rr[8], rr[19])
        return """<tr>
<td class="objno"><a target="cspace" href="%s">%s</a></td>
<input type="hidden" name="csid.%s" value="%s">
<td class="objname"><input type="hidden" name="onm.%s" value="">%s</td>
<td>

<table>

<tr class="monty">

<td>Count<br/>
<input class="xspan" type="text" size="10" name="ocn.%s" value="%s"></td>

<td>Cultural Group<br/>
<input class="xspan" type="text" size="40" name="cg.%s" value="%s"></td>

<td>Ethnographic File Code<br/>
<input class="xspan" type="text" size="40" name="fc.%s" value="%s"></td></td>

</tr>

<tr class="monty">

<td>Alt Num<br/>
<input class="xspan" type="text" size="40" name="anm.%s" value="%s"></td>

<td>Alt Num Type<br/>
%s</td>

<td>Field Collector<br/>
<input class="xspan" type="text" size="40" name="cl.%s" value="%s"></td>

</tr>

<tr class="monty">

<td>Object type<br/>
%s</td>

<td>Production person<br/>
<input class="xspan" type="text" size="40" name="pe.%s" value="%s"></td>

<td>Object Status<br/>
%s
</td>

</tr>

<tr class="monty">

<td>Date collected<br/>
<input class="xspan" type="text" size="40" name="dcol.%s" value="%s"></td>

<td>Production date<br/>
<input class="xspan" type="text" size="40" name="dprd.%s" value="%s"></td>

<td>Date depicted<br/>
<input class="xspan" type="text" size="40" name="ddep.%s" value="%s"></td>

</tr>

<tr class="monty">

<td>Materials<br/>
<input class="xspan" type="text" size="40" name="ma.%s" value="%s"></td>

<td>Taxon<br/>
<input class="xspan" type="text" size="40" name="ta.%s" value="%s"></td>

<td>Verbatim field collection place<br/>
<input class="xspan" type="text" size="40" name="vfcp.%s" value="%s"></td>

</tr>

<tr class="monty">

<td>Field collection place<br/>
<input class="xspan" type="text" size="40" name="cp.%s" value="%s"></td>

<td>Production Place<br/>
<input class="xspan" type="text" size="40" name="pp.%s" value="%s"></td>

<td>Place depicted<br/>
<input class="xspan" type="text" size="40" name="pd.%s" value="%s"></td>

</tr>

<tr>
<td colspan="10">Brief Description<br/>
<textarea cols="130" rows="5" name="bdx.%s">%s</textarea>
</td>
</tr>

</table>

</td>
</tr>""" % (
        link, cgi.escape(rr[3], True), rr[8], rr[8], rr[8], cgi.escape(rr[4], True),
        rr[8], rr[5],
        rr[8], cgi.escape(rr[7], True),
        rr[8], cgi.escape(rr[9], True),
        rr[8], cgi.escape(rr[18], True),
        altnumtypes,
        rr[8], cgi.escape(rr[16], True),
        objecttypes,
        rr[8], cgi.escape(rr[36], True),
        objstatuses,
        rr[8], cgi.escape(rr[29], True),
        rr[8], cgi.escape(rr[32], True),
        rr[8], cgi.escape(rr[34], True),
        rr[8], cgi.escape(rr[30], True),
        rr[8], cgi.escape(rr[33], True),
        rr[8], cgi.escape(rr[28], True),
        rr[8], cgi.escape(rr[6], True),
        rr[8], cgi.escape(rr[31], True),
        rr[8], cgi.escape(rr[35], True),
        rr[8], cgi.escape(rr[15], True)
        )


def setRefnames(refNames2find, fieldset, form, config, index):

    if fieldset in ['namedesc', 'fullmonty']:
        pass
    if fieldset in ['registration', 'fullmonty']:
        if not refNames2find.has_key(form.get('cl.' + index)):
            refNames2find[form.get('cl.' + index)] = cswaDB.getrefname('collectionobjects_common_fieldcollectors', form.get('cl.' + index), config)
    if fieldset in ['keyinfo', 'fullmonty']:
        if not refNames2find.has_key(form.get('cp.' + index)):
            refNames2find[form.get('cp.' + index)] = cswaDB.getrefname('places_common', form.get('cp.' + index), config)
        if not refNames2find.has_key(form.get('cg.' + index)):
            refNames2find[form.get('cg.' + index)] = cswaDB.getrefname('concepts_common', form.get('cg.' + index), config)
        if not refNames2find.has_key(form.get('fc.' + index)):
            refNames2find[form.get('fc.' + index)] = cswaDB.getrefname('concepts_common', form.get('fc.' + index), config)
    if fieldset in ['hsrinfo', 'fullmonty']:
        if not refNames2find.has_key(form.get('cp.' + index)):
            refNames2find[form.get('cp.' + index)] = cswaDB.getrefname('places_common', form.get('cp.' + index), config)
    if fieldset in ['places', 'fullmonty']:
        if not refNames2find.has_key(form.get('pp.' + index)):
            refNames2find[form.get('pp.' + index)] = cswaDB.getrefname('places_common', form.get('pp.' + index), config)
        if not refNames2find.has_key(form.get('cp.' + index)):
            refNames2find[form.get('cp.' + index)] = cswaDB.getrefname('places_common', form.get('cp.' + index), config)
        if not refNames2find.has_key(form.get('pd.' + index)):
            refNames2find[form.get('pd.' + index)] = cswaDB.getrefname('places_common', form.get('pd.' + index), config)
    if fieldset in ['objtypecm', 'fullmonty']:
        if not refNames2find.has_key(form.get('cm.' + index)):
            refNames2find[form.get('cm.' + index)] = cswaDB.getrefname('persons_common', form.get('cm.' + index), config)
        if not refNames2find.has_key(form.get('cp.' + index)):
            refNames2find[form.get('cp.' + index)] = cswaDB.getrefname('places_common', form.get('cp.' + index), config)
    if fieldset in ['fullmonty', 'mattax']:
        if not refNames2find.has_key(form.get('pe.' + index)):
            refNames2find[form.get('pe.' + index)] = cswaDB.getrefname('persons_common', form.get('pe.' + index), config)
        if not refNames2find.has_key(form.get('ma.' + index)):
            refNames2find[form.get('ma.' + index)] = cswaDB.getrefname('concepts_common', form.get('ma.' + index), config)
        if not refNames2find.has_key(form.get('ta.' + index)):
            refNames2find[form.get('ta.' + index)] = cswaDB.getrefname('taxon_common', form.get('ta.' + index), config)

    return refNames2find

if __name__ == '__main__':

    data = ['Regatta, A124, Mapcase Drawer 01', 'Regatta,0A124,0Mapcase0Drawer001:0',
            'xxx', '1-10080', 'Basket', '1',
            'Six Mile, Calaveras county, California', 'Eastern Miwok', 'ebb26dd3-52c9-42a3-9f90-5309933e4b2f', '',
            "urn:cspace:pahma.cspace.berkeley.edu:placeauthorities:name(place):item:name(pl1547482)'Six Mile, Calaveras county, California'",
            "urn:cspace:pahma.cspace.berkeley.edu:conceptauthorities:name(concept):item:name(ec1550590)'Eastern Miwok'",
            '', '', '', 'Small.', 'Samuel A. Barrett', 'Mrs. Phoebe Apperson Hearst', '189', 'original number',
            "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(447)'Samuel A. Barrett'",
            'Acc.216',
            "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(444)'Mrs. Phoebe Apperson Hearst'",
            '8cac5be5-4072-4257-a8ec-0bbb5ec761de', '3f8a27ec-f2b3-4902-920a-6f55e499e7ee', '', 'ethnography',
            'Natasha Johnson', 'California; Calaveras; Six Mile', '1906']
    html = formatRow({'rowtype': 'keyinfo', 'data': data}, {'fieldset': 'keyinfo'}, {})
    goodresult = """<tr>
<td class="objno"><a target="cspace" href="https://hostname/collectionspace/ui/institution/html/cataloging.html?csid=ebb26dd3-52c9-42a3-9f90-5309933e4b2f">1-10080</a></td>
<td class="objname">
<input class="objname" type="text" name="onm.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="Basket">
</td>
<td class="veryshortinput"><input class="veryshortinput" type="text" name="ocn.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="1"></td>
<td class="zcell">
<input type="hidden" name="oox.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="1-10080">
<input type="hidden" name="csid.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="ebb26dd3-52c9-42a3-9f90-5309933e4b2f">
<input class="xspan" type="text" size="26" name="cp.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="Six Mile, Calaveras county, California"></td>
<td class="zcell"><input class="xspan" type="text" size="26" name="cg.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value="Eastern Miwok"></td>
<td class="zcell"><input class="xspan" type="text" size="26" name="fc.ebb26dd3-52c9-42a3-9f90-5309933e4b2f" value=""></td>
</tr>"""
    if goodresult.replace('\n', '') == html.replace('\n', ''): print("keyinfo fieldset keyinfo ok")
