#!/usr/bin/env /var/www/venv/bin/python

import traceback
import cgitb; cgitb.enable()  # for troubleshooting
from toolbox.cswaConstants import selectWebapp
from toolbox.cswaUtils import *
from common.utils import loginfo

#reload(sys)
#sys.setdefaultencoding('utf-8')


def main(request, updateType, form, webappconfig):

    if request.user.is_authenticated:
        form['userdata'] = request.user
    else:
        return "<span style='color:chocolate'>You must be authenticated to use these Tools! Please sign in (upper right of this page).</span>", None


    update_action_label = form.get('action')
    checkServer = form.get('check')

    html = ''

    # if we don't know which tool was picked, have the user pick one
    if updateType == 'landing':
        html = selectWebapp(form, webappconfig)
        return html, None

    # if action has not been set, this is the first time through, and we need to set defaults. (only 2 right now!)
    if update_action_label == 'Login':
        form['dora'] = 'alive'

    # if location2 was not specified, default it to location1
    if str(form.get('lo.location2')) == '':
        form['lo.location2'] = form.get('lo.location1')

    # same for objects
    if str(form.get('ob.objno2')) == '':
        form['ob.objno2'] = form.get('ob.objno1')

    elapsedtime = time.time()

    loginfo('toolbox', f'start {updateType}', {}, request)
    html += starthtml(form, updateType, webappconfig)

    try:
        sys.stdout.flush()

        if checkServer == 'check server':
            print(serverCheck(form,webappconfig))
        else:
            if update_action_label == "Enumerate Objects":
                html += doEnumerateObjects(form,webappconfig)
            elif update_action_label == "Create Labels for Locations Only":
                html += doBarCodes(form,webappconfig)
            elif update_action_label == webappconfig.get(updateType, 'updateactionlabel'):
                if   updateType == 'packinglist':  html += doPackingList(form,webappconfig)
                elif updateType == 'movecrate':    html += doUpdateLocations(form,webappconfig)
                elif updateType == 'powermove':    html += doUpdateLocations(form,webappconfig)
                elif updateType == 'grpmove':      html += doUpdateLocations(form,webappconfig)
                elif updateType == 'barcodeprint': html += doBarCodes(form,webappconfig)
                elif updateType == 'inventory':    html += doUpdateLocations(form,webappconfig)
                elif updateType == 'moveobject':   html += doUpdateLocations(form,webappconfig)
                elif updateType == 'objinfo':      html += doUpdateKeyinfo(form,webappconfig)
                elif updateType == 'keyinfo':      html += doUpdateKeyinfo(form,webappconfig)
                elif updateType == 'grpinfo':      html += doUpdateKeyinfo(form,webappconfig)
                elif updateType == 'createobjects': html += doCreateObjects(form,webappconfig)
                elif updateType == 'bulkedit':     html += doBulkEdit(form,webappconfig)
                elif updateType == 'bedlist':      html += doBedList(form,webappconfig)
                elif updateType == 'advsearch':    html += doAdvancedSearch(form,webappconfig)
                elif updateType == 'governmentholdings': html += doListGovHoldings(form, webappconfig)
                #elif updateType == 'editrel':      html += doRelationsEdit(form,config)
                elif updateType == 'makegroup':    makeGroup(form,webappconfig)
                elif update_action_label == "Recent Activity":
                    viewLog(form,webappconfig)
            elif update_action_label == "Search":
                if   updateType == 'packinglist':  html += doLocationSearch(form,webappconfig,'nolist')
                elif updateType == 'movecrate':    html += doCheckMove(form,webappconfig)
                elif updateType == 'grpmove':      html += doCheckGroupMove(form,webappconfig)
                elif updateType == 'powermove':    html += doCheckPowerMove(form,webappconfig)
                elif updateType == 'barcodeprint':
                    if form.get('gr.group'):
                        html += doGroupSearch(form, webappconfig, 'list')
                    elif form.get('ob.objno1'):
                        html += doOjectRangeSearch(form, webappconfig)
                    else:
                        html += doLocationSearch(form, webappconfig, 'nolist')
                elif updateType == 'bedlist':      html += doComplexSearch(form,webappconfig,'select')
                elif updateType == 'bulkedit':     html += doBulkEditForm(form,webappconfig,'nolist')
                elif updateType == 'holdings':     html += doAuthorityScan(form,webappconfig)
                elif updateType == 'locreport':    html += doAuthorityScan(form,webappconfig)
                elif updateType == 'advsearch':    html += doComplexSearch(form,webappconfig,'select')
                elif updateType == 'inventory':    html += doLocationSearch(form,webappconfig,'list')
                elif updateType == 'keyinfo':      html += doLocationSearch(form,webappconfig,'list')
                elif updateType == 'objinfo':      html += doObjectSearch(form,webappconfig,'list')
                elif updateType == 'grpinfo':      html += doGroupSearch(form,webappconfig,'list')
                elif updateType == 'createobjects': html += doCreateObjects(form,webappconfig)
                elif updateType == 'moveobject':   html += doObjectSearch(form,webappconfig,'list')
                 #elif updateType == 'editrel':      html += doRelationsSearch(form,config)
                elif updateType == 'makegroup':    html += doComplexSearch(form,webappconfig,'select')

            elif update_action_label == "View Hierarchy":
                html += doHierarchyView(form,webappconfig)
            elif update_action_label == "View Holdings":
                html += doListGovHoldings(form,webappconfig)
            elif update_action_label in ['<<', '>>']:
                html += "<h3>Sorry not implemented yet! Please try again tomorrow!</h3>"
            else:
                pass
                # print("<h3>Unimplemented action %s!</h3>" % str(action))

    except Exception as e:
        sys.stderr.write("error! %s" % traceback.format_exc())
        # formatted_lines = traceback.format_exc().splitlines()
        # error_message = formatted_lines[-1]
        html += '''<h3><span class="error">So sorry! we have encountered a problem:</span></h3>
        <p>Can you please email <a href="mailto:cspace-support@lists.berkeley.edu?Subject=Webapp error: %s">cspace-support@lists.berkeley.edu</a> and let them know?
        Include the following error message and details of what you were doing (values entered in the page, etc.)</>
        <p><b>'''
        for message in e.args:
            html += message
            sys.stderr.write('error message: %s' % message)
        html += '</b></p>'

    elapsedtime = time.time() - elapsedtime

    loginfo('toolbox', f'end   {updateType}', {'elapsed_time': '%8.2f' % elapsedtime}, request)
    html += endhtml(form,webappconfig,elapsedtime)

    return html, ('%8.2f' % elapsedtime) + ' seconds'
