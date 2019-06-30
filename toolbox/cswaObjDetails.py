# -*- coding: UTF-8 -*-
import locale

locale.setlocale(locale.LC_ALL, 'en_US')

# the only other module: isolate postgres calls and connection
import toolbox.cswaDBobjdetails as DBquery


def formatField(label, condition, value, template, notentered):
    result = '<tr><td class="rightlabel"><b>%s:</b></td>\n' % label
    if condition is None:
        if value is None:
            result += '<td><span class="notentered">%s</span></span></td></tr>\n' % notentered
        else:
            result += '<td><span align="left">' + str(value) + "</span></td></tr>\n"
    else:
        if type(condition) == type([]):
            result += '<td><span align="left">'
            for rows in condition:
                for cell in rows:
                    if cell:
                        result += cell + ', '
                result += '<br/>'
            result += '</span></td></tr>\n'
        else:
            result += '<td><span align="left">' + template % str(condition) + "</span></td></tr>\n"
    return result


def doObjectDetails(form, config):
    html = ''
    scannedObjectNumber = form.get('ob.objectnumber')
    objresult = DBquery.getobjinfo(scannedObjectNumber, config)
    if objresult == None: objresult = 18 * [None]
    currlocresult = objresult[17]
    accresult = DBquery.getaccinfo(objresult[15], config)
    if accresult == None: accresult = 3 * [None]
    altnums = DBquery.getaltnums(objresult[16], config)
    if altnums == None: altnums = 3 * [None]
    ############## FIX BELOW: USE ID INSTEAD OF OBJECTNUMBER ##############
    allaltnumresult = DBquery.getallaltnums(scannedObjectNumber, config)
    assoccultures = DBquery.getassoccultures(objresult[16], config)
    ############## FIX BELOW: USE CSID INSTEAD OF OBJECTNUMBER ##############
    proddates = DBquery.getproddates(scannedObjectNumber, config)
    if proddates == None: proddates = 3 * [None]
    ############## FIX BELOW: USE CSID INSTEAD OF OBJECTNUMBER ##############
    objmedia = DBquery.getmedia(scannedObjectNumber, config)
    ############## FIX BELOW: USE CSID INSTEAD OF OBJECTNUMBER ##############
    parentinfo = DBquery.getparentinfo(scannedObjectNumber, config)
    if parentinfo == None: parentinfo = 13 * [None]
    parentaltnums = DBquery.getparentaltnums(parentinfo[12], config)
    if parentaltnums is None: parentaltnums = 4 * [None]
    parentaccinfo = DBquery.getparentaccinfo(parentinfo[2], config)
    if parentaccinfo == None: parentaccinfo = 3 * [None]
    ############## FIX BELOW: USE CSID INSTEAD OF OBJECTNUMBER ##############
    childinfo = DBquery.getchildinfo(scannedObjectNumber, config)
    if childinfo == None: childinfo = 4 * [None]
    childlocations = DBquery.getchildlocations(childinfo[2], config)
    if childlocations == None: childlocations = 4 * [None]

    html += '<div class="subheader">'
    if objresult[6] == None:
        objectname = '<i>no object name entered.</i>'
    else:
        objectname = objresult[6]
    html += '<a style="color: white;" href="https://pahma.cspace.berkeley.edu/collectionspace/ui/pahma/html/cataloging.html?csid=%s" target="_blank">%s</a> — %s' % (
    objresult[15], objresult[0], objectname)
    html += '</div>'

    html += """
    <div style="width:85%; float:left; ">
    <table width="100%">"""

    ######### Alternate Number #########
    html += '<tr><td class="rightlabel"><b>Alternate number(s):</b></td><td><span align="left">'
    if altnums[0] == None and parentaltnums[1] != None and str(objresult[10]) == 'yes':
        html += "<span class='notentered'>{on record for " + str(parentinfo[1]) + "}:  </span>" + str(parentaltnums[1]),
        if str(parentaltnums[2]) != 'None':
            html += " (" + (parentaltnums[2]),
        if str(parentaltnums[3]) != 'None':
            if str(parentaltnums[2]) != 'None':
                html += ", " + (parentaltnums[3]) + ")</span></td></tr>"
            else:
                html += "( " + (parentaltnums[3]) + ")</span></td></tr>"
        else:
            if parentaltnums[2] != None:
                html += ")</span></td></tr>"
            else:
                html += "</span></td></tr>"
    elif str(altnums[0]) == 'None' and str(parentaltnums[1]) == 'None':
        html += "<span class='notentered'>none entered</span></td></tr>"
    elif str(altnums[0]) == 'None' and str(objresult[10]) == 'no':
        html += "<span class='notentered'>none entered</span></td></tr>"
    else:
        html += str(altnums[0])
        if str(altnums[1]) != 'None':
            html += " (" + (altnums[1])
        if str(altnums[2]) != 'None':
            if str(altnums[1]) != 'None':
                html += ", " + (altnums[2]) + ")</span></td></tr>"
            else:
                html += "( " + (altnums[2]) + ")</span></td></tr>"
        else:
            if str(altnums[1]) != 'None':
                html += ")</span></td></tr>"
            else:
                html += "</span></td></tr>"

            ######### Current Location #########  NEED TO CONVERT getchildlocations TO FETCHALL()

    if currlocresult == None and str(objresult[10]) == 'no' and childlocations[3] != None:
        html += '<tr><td class="rightlabel"><b>Current location:</b></td><td><span align="left">%s : %s</span></td></tr>' % (
        childlocations[0], childlocations[3])
    else:
        html += '<tr><td class="rightlabel"><b>Current location:</b></td><td><span align="left">%s</span></td></tr>' % currlocresult

    html += formatField('Object count', objresult[3], objresult[3], '%s piece(s)', 'no count entered')
    html += formatField('Object type', objresult[1], parentinfo[3], '%s', 'PARENT: none entered')
    html += formatField('Collection manager(s)', objresult[14], parentinfo[11], '%s', 'none entered')
    html += formatField('All alternate number(s)', allaltnumresult, '', '%s (%s)', 'none entered')
    html += formatField('Brief Description', objresult[8], None, '%s', 'none entered')
    html += formatField('Distinguishing features', objresult[4], parentinfo[4], '%s', 'none entered')
    html += formatField('Ethnographic file code', objresult[9], parentinfo[7], '%s', 'none entered')
    ######### Associated Cultural Group #########  ADD PARENT
    html += formatField('Associated cultural group', assoccultures, '', '%s', 'none entered')
    #      for assocculture in assoccultures:
    #         html += str(assocculture[0]) + " "
    #         if str(assocculture[1]) <> 'None':
    #            html += "(" + str(assocculture[1]) + ") "
    #         if str(assocculture[2]) <> 'None':
    #            html += "(" + str(assocculture[2]) + ")<br/>"
    #         else:
    #            html += "<br/>"
    #
    #   html += "</span></td></tr>"

    ######### Production Date #########  ADD PARENT
    #html += formatField('Production date',proddates[1],proddates[2],'(%s)','%s','none entered')
    html += '<tr><td class="rightlabel"><b>Production date:</b></span></td><td><span align="left">'
    if str(proddates[1]) == 'None':
        html += '<span class="notentered">none entered</span></span></td></tr>'
    else:
        html += str(proddates[1])
        if str(proddates[2]) != 'None':
            html += " (" + (proddates[2]) + ")</span></td></tr>"

    html += formatField('Field collection place', objresult[13], parentinfo[10], '%s', 'none entered')
    html += formatField('Field collection place (vebatim)', objresult[12], parentinfo[9], '%s', 'none entered')
    html += formatField('Collector', objresult[2], parentinfo[5], '%s', 'none entered')
    html += formatField('Donor', accresult[1], parentaccinfo[1], '%s', 'none entered')
    link = '<a href="https://pahma.cspace.berkeley.edu/collectionspace/ui/pahma/html/acquisition.html?csid=%s" target="_blank">'
    html += formatField('Accession', accresult[0], parentaccinfo[0], link, 'none entered')
    html += formatField('PAHMA legacy catalog', objresult[11], parentinfo[8], '%s', 'none entered')

    html += "</table>"
    html += "</div>"

    ########## Trying to incorporate media ######### NEED TO SHOW PARENT MEDIA IF NO MEDIA
    html += """<div style="width:15%; float:left; ">"""
    if objmedia != None:
        for image in objmedia:
            #/blobs/be903851-a2a8-4eee-bf15/derivatives/Thumbnail/content
            #link = "https://pahma.cspace.berkeley.edu/cspace-services/blobs/%s/derivatives/%s/content"
            # use spiffy, new "public image service", to avoid having to re-authenticate user
            link = "https://webapps.cspace.berkeley.edu/pahma/imageserver/blobs/%s/derivatives/%s/content"
            thumb = link % (image[1], 'Thumbnail')
            original = link % (image[1], 'OriginalJpeg')
            html += '<div class="imagecell"><a href="%s" target="_blank"><img src="%s"></a></div>' % (original, thumb)
    else:
        html += "no related media"
    html += "</div>"
    html += '<div style="width: 100%; float:left;"><hr/></div>'

    # html += "<script>getLastFormElem().focus();</script>"
    return html


if __name__ == "__main__":
    # to test this module on the command line you have to pass in two cgi values:
    # $ python cswaObjDetails.py "ob.objectnumber=11-11&webapp=objectInfoDev"

    # this will load the config file and attempt to update some records in server identified
    # in that config file!
    import cgi
    from toolbox.cswaUtils import getConfig

    form = cgi.FieldStorage()
    config = getConfig(form)
    doObjectDetails(form, config)
