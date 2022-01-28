#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import csv, sys, time, os, datetime
import configparser
from os import path

SITE_ROOT = path.dirname(path.realpath(__file__))

#reload(sys)
# sys.setdefaultencoding('utf-8')

def getStyle(schemacolor1):
    return '''
<style type="text/css">
body { margin:10px 10px 0px 10px; font-family: Arial, Helvetica, sans-serif; }
table { }
td { padding-right: 10px; }
th { text-align: left ;color: #666666; font-size: 16px; font-weight: bold; padding-right: 20px;}
h2 { font-size:32px; padding:10px; margin:0px; border-bottom: none; }
h3 { font-size:24px; padding:10px; }
p { padding:10px 10px 10px 10px; }
li { text-align: left; list-style-type: none; }
a { text-decoration: none; }
button { font-size: 150%; width:85px; text-align: center; text-transform: uppercase;}
.monty { }
.cell { line-height: 1.0; text-indent: 2px; color: #666666; font-size: 16px;}
.enumerate { background-color: green; font-size:20px; color: #FFFFFF; font-weight:bold; vertical-align: middle; text-align: center; }
img#logo { float:left; height:50px; padding:10px 10px 10px 10px;}
.authority { color: #000000; background-color: #FFFFFF; font-weight: bold; font-size: 18px; }
.ncell { line-height: 1.0; cell-padding: 2px; font-size: 16px;}
.zcell { min-width:80px; cell-padding: 2px; font-size: 16px;}
.shortcell { width:180px; cell-padding: 2px; font-size: 16px;}
.objname { font-weight: bold; font-size: 16px; font-style: italic; min-width:200px; }
.objno { font-weight: bold; font-size: 16px; font-style: italic; }
.ui-tabs .ui-tabs-panel { padding: 0px; min-height:120px; }
.rdo { text-align: center; width:60px; }
.error {color:red;}
.warning {color:chocolate;}
.ok {color:green;}
.save { background-color: BurlyWood; font-size:20px; color: #000000; font-weight:bold; vertical-align: middle; text-align: center; }
.shortinput { font-weight: bold; width:150px; }
.subheader { background-color: ''' + schemacolor1 + '''; color: #FFFFFF; font-size: 24px; font-weight: bold; }
.smallheader { background-color: ''' + schemacolor1 + '''; color: #FFFFFF; font-size: 12px; font-weight: bold; }
.veryshortinput { width:60px; }
.xspan { color: #000000; background-color: #FFFFFF; font-weight: bold; font-size: 12px; }
th[data-sort]{ cursor:pointer; }
.littlebutton {color: #FFFFFF; background-color: gray; font-size: 11px; padding: 2px; cursor: pointer; }
.imagecell { padding: 8px ; align: center; }
.rightlabel { text-align: right ; vertical-align: top; padding: 2px 12px 2px 2px; width: 30%; }
.objtitle { font-size:28px; float:left; padding:4px; margin:0px; border-bottom: thin dotted #aaaaaa; color: #000000; }
.objsubtitle { font-size:28px; float:left; padding:2px; margin:0px; border-bottom: thin dotted #aaaaaa; font-style: italic; color: #999999; }
.notentered { font-style: italic; color: #999999; }
</style>
'''

def tricoderUsers():
    #*** Ape prohibited list code to get table ***
    return{'A1732177': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7827)'Michael T. Black'",
              'A1676856': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8700)'Raksmey Mam'",
              'A0951620': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7475)'Leslie Freund'",
              'A1811681': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'",
              'A2346921': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9090)'Corri MacEwen'",
              'A2055958': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8683)'Alicja Egbert'",
              'A2507976': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8731)'Tya Ates'",
              'A2247942': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9185)'Alex Levin'",
              'A2346563': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9034)'Martina Smith'",
              'A1728294': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7420)'Jane L. Williams'",
              'A1881977': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8724)'Allison Lewis'",
              'A2472847': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(RowanGard1342219780674)'Rowan Gard'",
              'A1687900': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7500)'Elizabeth Minor'",
              'A2472958': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(AlexanderJackson1345659630608)'Alexander Jackson'",
              'A2503701': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(GavinLee1349386412719)'Gavin Lee'",
              'A2504029': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(RonMartin1349386396342)'Ron Martin' ",
              'A1148429': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8020)'Paolo Pellegatti'",
              'A0904690': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7267)'Victoria Bradshaw'",
              'A2525169': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(GrainneHebeler1354748670308)'Grainne Hebeler'",
              '20271721': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(KatieFleming1353023599564)'KatieFleming'",
              'A2266779': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(KatieFleming1353023599564)'KatieFleming'",
              'A2204739': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(PaigeWalker1351201763000)'PaigeWalker'",
              'A0701434': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7248)'Madeleine W. Fang'",
              'A2532024': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(LindaWaterfield1358535276741)'LindaWaterfield'",
              'A2581770': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(JonOligmueller1372192617217)'JonOligmueller'"}


def infoHeaders(fieldSet):
    if fieldSet == 'keyinfo':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Field Collection Place</th>
      <th>Cultural Group</th>
      <th>Ethnographic File Code</th>
    </tr>"""
    elif fieldSet == 'namedesc':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th></th>
      <th style="text-align:center">Brief Description</th>
    </tr>"""
    elif fieldSet == 'registration':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Alt Num</th>
      <th>Alt Num Type</th>
      <th>Field Collector</th>
      <th>Object Status</th>
      <th>Donor</th>
      <th>Accession</th>
    </tr>"""
    elif fieldSet == 'hsrinfo':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Count Note</th>
      <th>Field Collection Place</th>
      <th style="text-align:center">Brief Description</th>
    </tr>"""
    elif fieldSet == 'objtypecm':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Object Type</th>
      <th>Collection Manager</th>
      <th>Field Collection Place</th>
      <th>Legacy Department</th>
      <th>Object Status</th>
      <th></th>
    </tr>"""
    elif fieldSet == 'collection':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Collection</th>
    </tr>"""
    elif fieldSet == 'placeanddate':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Verbatim field collection place</th>
      <th>Field collection date</th>
    </tr>"""
    elif fieldSet == 'places':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Verbatim field collection place</th>
      <th>Field collection place</th>
      <th>Production Place</th>
      <th>Place depicted</th>
    </tr>"""
    elif fieldSet == 'dates':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Production date</th>
      <th>Field collection date</th>
      <th>Date depicted</th>
    </tr>"""
    elif fieldSet == 'mattax':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Materials</th>
      <th>Taxon</th>
      <th style="text-align:center">Brief Description</th>
    </tr>"""
    elif fieldSet == 'student':
        return """
    <table><tr>
      <th>Accession #</th>
      <th>Scientific name</th>
      <th>Country</th>
      <th>State</th>
      <th>County</th>
      <th>Project Code</th>
      <th>Media</th>
      <!-- th style="text-align:center">Brief Description</th -->
    </tr>"""
    elif fieldSet == 'fullmonty':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Fields</th>
    </tr>"""
    else:
        return "<table><tr>DEBUG</tr>"

def getProhibitedLocations(config, request):
    #fileName = config.get('files','prohibitedLocations')
    fileName = (os.path.join('.' + request.path + 'cfgs','prohibitedLocations.csv'))
    locList = []
    try:
        with open(fileName, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter="\t")
            for row in csvreader:
                locList.append(row[0])
    except:
        print('FAILED to load prohibited locations')
        raise

    return locList


def getHandlers(form, institution):
    selected = form.get('handlerRefName')


    if institution == 'bampfa':
        handlerlist = [
            ('Kelly Bennett', 'KB'),
            ('Gary Bogus', 'GB'),
            ('Lisa Calden', 'LC'),
            ('Stephanie Cannizzo', 'SC'),
            ('Laura Hansen', 'LH'),
            ('Jenny Heffernon', 'JH'),
            ('Tracy Jones', 'TJ'),
            ('Michael Meyers', 'MM'),
            ('Scott Orloff', 'SO'),
            ('Pamela Pack', 'PP'),
            ('Julia White', 'JW'),
        ]
    else:

        handlerlist = [
            ("Michael T. Black", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7827)'Michael T. Black'"),
            ("Madeleine Fang", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7248)'Madeleine W. Fang'"),
            ("Leslie Freund", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7475)'Leslie Freund'"),
            ("Natasha Johnson", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'"),
            ("Linda Waterfield", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(LindaWaterfield1358535276741)'Linda Waterfield'"),
        ]

    handlers = '''
          <select class="cell" name="handlerRefName">
              <option value="None">Select a handler</option>'''

    for handler in handlerlist:
        #print(handler)
        handlerOption = """<option value="%s">%s</option>""" % (handler[1], handler[0])
        #print("xxxx",selected)
        if selected and str(selected) == handler[1]:
            handlerOption = handlerOption.replace('option', 'option selected')
        handlers = handlers + handlerOption

    handlers += '\n      </select>'
    return handlers, selected


def getReasons(form, institution):
    reason = form.get('reason')

    if institution == 'bampfa':
        reasons = '''
        <select class="cell" name="reason">
        <options>
        <option value="None" default="yes">(none selected)</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015Inventory1422385313472)'2015 Inventory'" selected>2015 Inventory</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015MoveStaging1423179160443)'2015 Move Staging'">2015 Move Staging</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015Packing1422385332220)'2015 Packing'">2015 Packing</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason001)'Conservation'">Conservation</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(DataCleanUp1416598052252)'Data Clean Up'">Data Clean Up</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason002)'Exhibition'">Exhibition</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason003)'Inventory'">Inventory</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason004)'Loan'">Loan</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason005)'New Storage Location'">New Storage Location</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason006)'Photography'">Photography</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(Reconciled1458582185744)'Reconciled'">Reconciled</option>
        <option value="urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason007)'Research'">Research</option>
        </options>
        </select>

        '''
    else:
        # these are for PAHMA
        reasons = '''
    <select class="cell" name="reason">
    <option value="None">(none selected)</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason44)'(not entered)'">(not entered)</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason01)'Inventory'">Inventory</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason02)'General Collections Management'">General Collections Management</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason03)'Research'">Research</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason34)'Native Am Adv Grp Visit'">Native Am Adv Grp Visit</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason05)'per shelf label'">per shelf label</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason06)'New Home Location'">New Home Location</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason07)'Loan'">Loan</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason08)'Exhibit'">Exhibit</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason09)'Class Use'">Class Use</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason10)'Photo Request'">Photo Request</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason11)'Tour'">Tour</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason12)'Conservation'">Conservation</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason13)'cultural heritage'">cultural heritage</option>
    <option value="">----------------------------</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason14)'Object relocation'">Object relocation</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason16)'2012 HGB surge pre-move inventory'">2012 HGB surge pre-move inventory</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason17)'2014 Marchant inventory and move'">2014 Marchant inventory and move</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason18)'Asian Textile Grant'">Asian Textile Grant</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason19)'Basketry Rehousing Proj'">Basketry Rehousing Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason20)'BOR Proj'">BOR Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason21)'Building Maintenance: Seismic'">Building Maintenance: Seismic</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason22)'California Archaeology Proj'">California Archaeology Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason23)'Cat. No. Issue Investigation'">Cat. No. Issue Investigation</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason24)'Duct Cleaning Proj'">Duct Cleaning Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason25)'Federal Curation Act'">Federal Curation Act</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason26)'Fire Alarm Proj'">Fire Alarm Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason27)'First Time Storage'">First Time Storage</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason28)'Found in Collections'">Found in Collections</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason29)'Hearst Gym Basement move to Kroeber 20A'">Hearst Gym Basement move to Kroeber 20A</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason30)'HGB Surge'">HGB Surge</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason31)'Kro20Mezz LWeapon Proj 2011'">Kro20Mezz LWeapon Proj 2011</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason32)'Kroeber 20A move to Regatta'">Kroeber 20A move to Regatta</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason33)'Marchant Flood 12/2007'">Marchant Flood 12/2007</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason04)'NAGPRA'">NAGPRA</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason35)'NEH Egyptian Collection Grant'">NEH Egyptian Collection Grant</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason36)'Regatta move-in'">Regatta move-in</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason37)'Regatta pre-move inventory'">Regatta pre-move inventory</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason38)'Regatta pre-move object prep.'">Regatta pre-move object prep.</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason39)'Regatta pre-move staging'">Regatta pre-move staging</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason40)'SAT grant'">SAT grant</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason15)'spot inventory'">spot inventory</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason41)'Temporary Storage'">Temporary Storage</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason42)'Textile Rehousing Proj'">Textile Rehousing Proj</option>
    <option value="urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(reasonformove):item:name(movereason43)'Yoruba MLN Grant'">Yoruba MLN Grant</option>
    </select>
    '''

    reasons = reasons.replace(('option value="%s"' % reason), ('option selected value="%s"' % reason))
    return reasons, reason



def getLegacyDepts(form, csid, ld):
    selected = form.get('legacydept')

    legacydeptlist = [
        ("Audio recordings", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment01)'Audio recordings'"),
        ("Casts and molds", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment02)'Casts and molds'"),
        ("Cat. 1 - California (archaeology and ethnology)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment03)'Cat. 1 - California (archaeology and ethnology)'"),
        ("Cat. 2 - North America (except Mexico and Central America)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment04)'Cat. 2 - North America (except Mexico and Central America)'"),
        ("Cat. 3 - Mexico, Central America, and Caribbean Area", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment05)'Cat. 3 - Mexico, Central America, and Caribbean Area'"),
        ("Cat. 4 - South America (Uhle Collection)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment06)'Cat. 4 - South America (Uhle Collection)'"),
        ("Cat. 5 - Africa (except the Hearst Reisner Egyptian Collection)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment07)'Cat. 5 - Africa (except the Hearst Reisner Egyptian Collection)'"),
        ("Cat. 6 - Ancient Egypt (the Hearst Reisner Egyptian Collection)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment08)'Cat. 6 - Ancient Egypt (the Hearst Reisner Egyptian Collection)'"),
        ("Cat. 7 - Europe (incl. Russia west of Urals, north of Caucasus)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment09)'Cat. 7 - Europe (incl. Russia west of Urals, north of Caucasus)'"),
        ("Cat. 8 - Classical Mediterranean regions", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment12)'Cat. 8 - Classical Mediterranean regions'"),
        ("Cat. 9 - Asia (incl. Russia east of Urals)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment13)'Cat. 9 - Asia (incl. Russia east of Urals)'"),
        ("Cat. 10 - Philippine Islands", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment14)'Cat. 10 - Philippine Islands'"),
        ("Cat. 11 - Oceania (incl. Australia)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment15)'Cat. 11 - Oceania (incl. Australia)'"),
        ("Cat. 13 - Photographic prints (without negatives)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment16)'Cat. 13 - Photographic prints (without negatives)'"),
        ("Cat. 15 - Photographic negatives", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment17)'Cat. 15 - Photographic negatives'"),
        ("Cat. 16 - South America (except Uhle Collection)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment18)'Cat. 16 - South America (except Uhle Collection)'"),
        ("Cat. 17 - Drawings and Paintings", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment19)'Cat. 17 - Drawings and Paintings'"),
        ("Cat. 18 - Malaysia (incl. Indonesia, excl. Philippine Islands)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment20)'Cat. 18 - Malaysia (incl. Indonesia, excl. Philippine Islands)'"),
        ("Cat. 22 - Rubbings of Greek &amp; Latin Inscriptions", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment21)'Cat. 22 - Rubbings of Greek &amp; Latin Inscriptions'"),
        ("Cat. 23 - No provenience (most of catalog deleted)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment22)'Cat. 23 - No provenience (most of catalog deleted)'"),
        ("Cat. 25 - Kodachrome color transparencies", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment23)'Cat. 25 - Kodachrome color transparencies'"),
        ("Cat. 26 - Motion picture film", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment24)'Cat. 26 - Motion picture film'"),
        ("Cat. 28 - unknown (retired catalog)", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment25)'Cat. 28 - unknown (retired catalog)'"),
        ("Cat. B - Barr collection", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment26)'Cat. B - Barr collection'"),
        ("Cat. Bascom", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment27)'Cat. Bascom'"),
        ("Cat. E", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment28)'Cat. E'"),
        ("Cat. K - Kelly collection", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment29)'Cat. K - Kelly collection'"),
        ("Cat. L - Lillard Collection", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment30)'Cat. L - Lillard Collection'"),
        ("Cat. NO", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment31)'Cat. NO'"),
        ("Cat. TB", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment32)'Cat. TB'"),
        ("Faunal Remains", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment33)'Faunal Remains'"),
        ("Human Remains", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment34)'Human Remains'"),
        ("Loans In", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment35)'Loans In'"),
        ("Maps", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment36)'Maps'"),
        ("Mixed faunal and human remains", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment37)'Mixed faunal and human remains'"),
        ("Mounts", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment38)'Mounts'"),
        ("NAGPRA-associated Funerary Objects", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment39)'NAGPRA-associated Funerary Objects'"),
        ("Registration", "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaTmsLegacyDepartments):item:name(pahmaTMSLegacyDepartment40)'Registration'")
    ]

    legacydepts = \
          '''<select class="cell" name="ld.''' + csid + '''">
              <option value="None">Select a legacy department</option>'''

    for legacydept in legacydeptlist:
        if legacydept[1] == ld:
            legacydeptOption = """<option value="%s" selected>%s</option>""" % (legacydept[1], legacydept[0])
        else:
            legacydeptOption = """<option value="%s">%s</option>""" % (legacydept[1], legacydept[0])
        legacydepts = legacydepts + legacydeptOption

    legacydepts += '\n      </select>'
    return legacydepts, selected


def selectWebapp(form, webappconfig):

    if form.get('webapp') == 'switchapp':
        #sys.stderr.write('%-13s:: %s' % ('switchapp','looking for creds..'))
        username = form.get('csusername')
        password = form.get('cspassword')
        payload = '''
            <input type="hidden" name="checkauth" value="true">
            <input type="hidden" name="csusername" value="%s">
            <input type="hidden" name="cspassword" value="%s">''' % (username, password)
    else:
        payload = ''


    programName = ''
    apptitles = {}
    serverlabels = {}
    badconfigfiles = ''


    tools = webappconfig.get('tools','availabletools')
    tools = tools.replace('\n','').split(',')
    for tool in tools:
        if tool == 'landing':
            continue
        try:
            # check to see that all the needed values are available...
            logo = webappconfig.get('info','logo')
            schemacolor1 = webappconfig.get('info','schemacolor1')
            institution = webappconfig.get('info','institution')
            serverlabel = webappconfig.get('info','serverlabel')

            apptitle = webappconfig.get(tool,'apptitle')
            updateactionlabel = webappconfig.get(tool,'updateactionlabel')
            updateType = webappconfig.get(tool,'updatetype')
            apptitles[apptitle] = updateType
        except:
            badconfigfiles += '<tr><td>%s</td></tr>' % tool

    line = '<table>\n'

    for apptitle in sorted(apptitles.keys()):
            line += '<tr><td><a href="%s">%s</a></td></tr>\n' % (apptitles[apptitle], apptitle)

    if badconfigfiles != '':
        line += '<tr><td colspan="2"><h2>%s</h2></td></tr>' % 'bad config files'
        line += badconfigfiles

    line += '</table>\n'

    return line


def getPrinters(form):
    selected = form.get('printer')

    printerlist = [
        ("MA1", "cluster1"),
        ("Regatta", "cluster2")
    ]

    printers = '''
          <select class="cell" name="printer">
              <option value="None">Select a printer</option>'''

    for printer in printerlist:
        printerOption = """<option value="%s">%s</option>""" % (printer[1], printer[0])
        if selected and str(selected) == printer[1]:
            printerOption = printerOption.replace('option', 'option selected')
        printers += printerOption

    printers += '\n      </select>'
    return printers, selected, printerlist


def getFieldset(form, institution):
    selected = form.get('fieldset')

    if institution == 'bampfa':
        fields = [
            ("Collection", "collection"),
        ]
    elif institution == 'ucjeps':
        fields = [
            ("Student Entry", "student"),
        ]
    else:
        fields = [
            ("Key Info", "keyinfo"),
            ("Name & Desc.", "namedesc"),
            ("Registration", "registration"),
            ("HSR Info", "hsrinfo"),
            ("Object Type/CM", "objtypecm"),
            ("Place and Date", "placeanddate"),
            ("Places", "places"),
            ("Dates", "dates"),
            ("Material and Taxon", "mattax"),
            ("Full Monty", "fullmonty"),
        ]

    fieldset = '''
          <select class="cell" name="fieldset">'''

    for field in fields:
        fieldsetOption = """<option value="%s">%s</option>""" % (field[1], field[0])
        if selected and str(selected) == field[1]:
            fieldsetOption = fieldsetOption.replace('option', 'option selected')
        fieldset += fieldsetOption

    fieldset += '\n      </select>'
    return fieldset, selected


def getHierarchies(form, known_authorities):
    selected = form.get('authority')

    # this is a list of all the authorities the viewer knows how to handle.
    # the list of authorities for an institution is a parm in the .cfg file for
    # the hierarchy viewer and is passed in as 'authorities'
    authoritylist = [
        ("Concept", "concept"),
        ("Ethnographic Culture", "concept"),
        ("Places", "places"),
        ("Archaeological Culture", "archculture"),
        ("Ethnographic File Codes", "ethusecode"),
        ("Materials", "material_ca"),
        ("Taxonomy", "taxonomy"),
        ("Object Name", "objectname")
    ]

    authorities = '''
<select class="cell" name="authority">
<option value="None">Select an authority</option>'''

    #sys.stderr.write('selected %s\n' % selected)
    for authority in authoritylist:
        if authority[0] in known_authorities:
            authorityOption = """<option value="%s">%s</option>""" % (authority[1], authority[0])
            #sys.stderr.write('check hierarchy %s %s\n' % (authority[1], authority[0]))
            if selected == authority[1]:
                #sys.stderr.write('found hierarchy %s %s\n' % (authority[1], authority[0]))
                authorityOption = authorityOption.replace('option', 'option selected')
            authorities = authorities + authorityOption

    authorities += '\n </select>'
    return authorities, selected


def getAltNumTypes(form, csid, ant):
    selected = form.get('altnumtype')

    altnumtypelist = [
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum00)'additional number'", "additional number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum17)'associated catalog number'", "associated catalog number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum01)'attributed PAHMA number'", "attributed PAHMA number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum02)'burial number'", "burial number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(featurenumber1585675795833)'feature number'", "feature number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum18)'field number'", "field number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum03)'moac subobjid'", "moac subobjid"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum04)'museum number (recataloged to)'", "museum number (recataloged to)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum16)'(null)'", "(null)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum19)'original number'", "original number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum20)'previous museum number (recataloged from)'", "previous museum number (recataloged from)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum05)'previous number'", "previous number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum06)'previous number (Albert Bender’s number)'", "previous number (Albert Bender's number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum21)'previous number (Anson Blake’s number)'", "previous number (Anson Blake's number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum07)'previous number (Bascom’s number)'", "previous number (Bascom’s number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum08)'previous number (collector's original number)'", "previous number (collector's original number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum09)'previous number (Design Dept.)'", "previous number (Design Dept.)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum22)'previous number (donor's original number)'", "previous number (donor's original number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum10)'previous number (Lila M. O'Neale)'", "previous number (Lila M. O'Neale)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum11)'previous number (MVC number, Mossman-Vitale collection)'", "previous number (MVC number)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum12)'previous number (UCAS: University of California Archaeological Survey)'", "previous number (UCAS)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum23)'previous number (UC Paleontology Department)'", "previous number (UC Paleontology Department)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(referencenumber1506531301497)'reference number'", "reference number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum13)'song number'", "song number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum14)'tag'", "tag"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum24)'tb (temporary basket) number'", "tb (temporary basket) number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaaltnumber):item:name(altnum15)'temporary number'", "temporary number")
    ]

    altnumtypes = '''<select class="cell" name="ant.''' + csid + '''">
              <option value="None">Select a number type</option>'''

    for altnumtype in altnumtypelist:
        if altnumtype[0] == ant:
            altnumtypeOption = """<option value="%s" selected>%s</option>""" % (altnumtype[0], altnumtype[1])
        else:
            altnumtypeOption = """<option value="%s">%s</option>""" % (altnumtype[0], altnumtype[1])
        altnumtypes = altnumtypes + altnumtypeOption

    altnumtypes += '\n      </select>'
    return altnumtypes, selected


def getObjectStatuses(form, csid, ant):
    selected = form.get('objectstatus')

    objectstatuslist = [
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses02)'accessioned'",
            "accessioned"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses01)'accession status unclear'",
            "accession status unclear"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses03)'culturally affiliated'",
            "culturally affiliated"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses04)'culturally unaffiliated'",
            "culturally unaffiliated"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses05)'deaccessioned'",
            "deaccessioned"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses06)'destroyed'",
            "destroyed"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses07)'destructive analysis'",
            "destructive analysis"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses08)'discarded'",
            "discarded"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses09)'exchanged'",
            "exchanged"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses33)'held in trust'",
            "held in trust"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses20)'in loan (=borrowed)'",
            "in loan (=borrowed)"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses10)'intended for repatriation'",
            "intended for repatriation"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses11)'intended for transfer'",
            "intended for transfer"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses12)'irregular Museum number'",
            "irregular Museum number"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses13)'missing'",
            "missing"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses14)'missing in inventory'",
            "missing in inventory"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses15)'not cataloged'",
            "not cataloged"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses16)'not located'",
            "not located"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses17)'not received'",
            "not received"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses18)'number not used'",
            "number not used"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses19)'object mount'",
            "object mount"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses32)'on deposit'",
            "on deposit"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses21)'partially deaccessioned'",
            "partially deaccessioned"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses22)'partially exchanged'",
            "partially exchanged"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses23)'partially recataloged'",
            "partially recataloged"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses24)'pending repatriation'",
            "pending repatriation"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses25)'recataloged'",
            "recataloged"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses26)'red-lined'",
            "red-lined"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses27)'repatriated'",
            "repatriated"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses28)'returned loan object'",
            "returned loan object"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses29)'sold'",
            "sold"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses30)'stolen'",
            "stolen"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses31)'transferred'",
            "transferred"),
        ("urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(pahmaObjectStatuses):item:name(pahmaObjectStatuses00)'(unknown)'",
            "(unknown)"),
    ]

    objectstatuses = '''<select class="cell" name="obs.''' + csid + '''">
        <option value="None">Select an object status</option>'''

    for objectstatus in objectstatuslist:
        if objectstatus[0] == ant:
            objectstatusOption = """<option value="%s" selected>%s</option>""" % (objectstatus[0], objectstatus[1])
        else:
            objectstatusOption = """<option value="%s">%s</option>""" % (objectstatus[0], objectstatus[1])
        objectstatuses = objectstatuses + objectstatusOption

    objectstatuses += '\n      </select>'
    return objectstatuses, selected


def getObjType(form, csid, ot):
    selected = form.get('objectType')

    objtypelist = [ \
        ("none (Registration)",
         "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(objecttype):item:name(objtype01)'none (Registration)'"),
        ("archaeology",
         "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(objecttype):item:name(objtype02)'archaeology'"),
        ("ethnography",
         "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(objecttype):item:name(objtype03)'ethnography'"),
        ("indeterminate",
         "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(objecttype):item:name(objtype06)'indeterminate'"),
        ("unknown",
         "urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(objecttype):item:name(objtype07)'unknown'")
    ]

    objtypes = \
          '''<select class="cell" name="ot.''' + csid + '''">
              <option value="None">Select an object type</option>'''

    for objtype in objtypelist:
        if objtype[1] == ot:
            objtypeOption = """<option value="%s" selected>%s</option>""" % (objtype[1], objtype[0])
        else:
            objtypeOption = """<option value="%s">%s</option>""" % (objtype[1], objtype[0])
        objtypes = objtypes + objtypeOption

    objtypes += '\n      </select>'
    return objtypes, selected


def getCollMan(form, csid, cm):
    selected = form.get('collMan')

    collmanlist = [ \
        ("Natasha Johnson", "Natasha Johnson"),
        ("Leslie Freund", "Leslie Freund"),
        ("Alicja Egbert", "Alicja Egbert"),
        ("Victoria Bradshaw", "Victoria Bradshaw"),
        ("Uncertain", "uncertain"),
        ("None (Registration)", "No collection manager (Registration)")
    ]

    collmans = \
          '''<select class="cell" name="cm.''' + csid + '''">
              <option value="None">Select a collection manager</option>'''

    for collman in collmanlist:
        if collman[1] == cm:
            collmanOption = """<option value="%s" selected>%s</option>""" % (collman[1], collman[0])
        else:
            collmanOption = """<option value="%s">%s</option>""" % (collman[1], collman[0])
        collmans = collmans + collmanOption

    collmans += '\n      </select>'
    return collmans, selected


def getAgencies(form):
    selected = form.get('agency')

    agencylist = [ \
        ("Bureau of Indian Affairs", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8452)"),
        ("Bureau of Land Management", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3784)"),
        ("Bureau of Reclamation", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(6392)"),
        ("California Department of Transportation", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9068)"),
        ("California State Parks", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8594)"),
        ("East Bay Municipal Utility District", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(EastBayMunicipalUtilityDistrict1370388801890)"),
        ("National Park Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(1533)"),
        ("United States Air Force", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesAirForce1369177133041)"),
        ("United States Army", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3021)"),
        ("United States Coast Guard", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesCoastGuard1342641628699)"),
        ("United States Fish and Wildlife Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesFishandWildlifeService1342132748290)"),
        ("United States Forest Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3120)"),
        ("United States Marine Corps", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesMarineCorps1365524918536)"),
        ("United States Navy", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9079)"),
        ("U.S. Army Corps of Engineers", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9133)"),
    ]

    agencies = '''
<select class="cell" name="agency">
<option value="None">Select an agency</option>'''

    for agency in agencylist:
        agencyOption = """<option value="%s">%s</option>""" % (agency[1], agency[0])
        if selected == agency[1]:
            agencyOption = agencyOption.replace('option', 'option selected')
        agencies += agencyOption

    agencies += '\n </select>'
    return agencies, selected

def getIntakeFields(fieldset):

    if fieldset == 'intake':

        return [
            ('TR', 20, 'tr','31','fixed'),
            ('Number of Objects:', 5, 'numobjects','1','text'),
            ('Source:', 40, 'pc.source','','text'),
            ('Date in:', 30, 'datein',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'text'),
            ('Receipt?', 40, 'receipt','','checkbox'),
            ('Location:', 40, 'lo.location','','text'),
            ('Disposition:', 30, 'disposition','','text'),
            ('Artist/Title/Medium', 10, 'atm','','text'),
            ('Purpose:', 40, 'purpose','','text')
        ]
    elif fieldset == 'objects':

        return [
            ('ID number', 30, 'id','','text'),
            ('Title', 30, 'title','','text'),
            ('Comments', 30, 'comments','','text'),
            ('Artist', 30, 'pc.artist','','text'),
            ('Creation date', 30, 'cd','','text'),
            ('Creation technique', 30, 'ct','','text'),
            ('Dimensions', 30, 'dim','','text'),
            ('Responsible department', 30, 'rd','','text'),
            ('Computed current location', 30, 'lo.loc','','text')
            ]


def getHeader(updateType, institution):
    if updateType == 'inventory':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th>Found</th>
      <th style="width:60px; text-align:center;">Not Found</th>
      <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Found</th>
      <th style="width:60px; text-align:center;">Not Found</th>
      <th>Notes</th>
    </tr>"""
    elif updateType == 'movecrate':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move" checked/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move"/></th>
      <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move" checked/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move"/></th>
      <th>Notes</th>
    </tr>"""

    elif updateType == 'powermove':
        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th>Title</th>
      <th>Artist</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move"/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move" checked/></th>
     <th>Notes</th>
    </tr>"""
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th style="width:60px; text-align:center;">Move <input type="radio" name="check-move" id="check-move"/></th>
      <th style="width:60px; text-align:center;">Don't Move  <input type="radio" name="check-move" id="check-move" checked/></th>
     <th>Notes</th>
    </tr>"""


    elif updateType == 'packinglist':

        if institution == 'bampfa':
            return """
    <table><tr>
      <th>ID number</th>
      <th style="width:150px;">Title</th>
      <th>Artist</th>
      <th>Medium</th>
      <th>Dimensions</th>
      <th>Credit Line</th>
    </tr>
        """
        else:
            return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Field Collection Place</th>
      <th>Cultural Group</th>
      <th>Ethnographic File Code</th>
      <th></th>
    </tr>"""
    elif updateType == 'packinglistbyculture':
        return """
    <table><tr>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th width="150px;">Location</th>
      <th>Field Collection Place</th>
      <th></th>
    </tr>"""
    elif updateType == 'moveobject':
        return """
    <table><tr>
      <th>Move?</th>
      <th>Museum #</th>
      <th>Object name</th>
      <th>Count</th>
      <th>Location</th>
    </tr>"""
    elif 'bedlist' in updateType:
        if 'standard' in updateType:
            header = """
    <table class="tablesorter-blue" id="sortTable%s"><thead>
    <tr>
      <th data-sort="float">Accession</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Taxonomic Name</th>
      <th data-sort="string">Rare?</th>
      <th data-sort="string">Accession<br/>Dead?</th>
      %s
    </tr></thead><tbody>"""
        else:
            header = """
    <table class="tablesorter-blue" id="sortTable%s"><thead>
    <tr>
      <th data-sort="float">Accession Number</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Scientific Name</th>
      <th data-sort="string">Collection Location Information</th>
      <th data-sort="string">Notes</th>
      %s
    </tr></thead><tbody>"""
        if 'none' in updateType:
            return header % ('%s', '<th>Garden Location</th>')
        else:
            return header % ('%s', '')
    elif updateType in ['locreport', 'holdings', 'advsearch']:
        return """
    <table class="tablesorter-blue" id="sortTable"><thead><tr>
      <th data-sort="float">Accession</th>
      <th data-sort="string">Taxonomic Name</th>
      <th data-sort="string">Family</th>
      <th data-sort="string">Garden Location</th>
      <th data-sort="string">Locality</th>
      <th data-sort="string">Rare?</th>
      <th data-sort="string">Accession<br/>Dead?</th>
    </tr></thead><tbody>"""
    elif updateType == 'keyinfoResult' or updateType == 'objinfoResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Status</th>
      <th>CSID</th>
    </tr>"""
    elif updateType == 'inventoryResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Updated Inventory Status</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'barcodeprint':
        return """
    <table width="100%"><tr>
      <th>Location</th>
      <th>Objects found</th>
      <th>Barcode Filename</th>
      <th>Notes</th>
    </tr>"""
    elif updateType == 'barcodeprintlocations':
        return """
    <table width="100%"><tr>
      <th>Locations listed</th>
      <th>Barcode Filename</th>
    </tr>"""
    elif updateType == 'upload':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'intakeValues':
        return """
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>"""
    elif updateType == 'intakeResult':
        return """
    <table width="100%" border="1">
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""
    elif updateType == 'intakeObjects':
        return """
    <tr>
      <th>Museum #</th>
      <th>Note</th>
      <th>Update status</th>
    </tr>"""


if __name__ == '__main__':

    def handleResult(result,header):
        header = '\n<tr><td>%s<td>' % header
        if type(result) == type(()) and len(result) >= 2:
            return header + result[0]
        elif type(result) == type('string'):
            return header + result
        else:
            print("handleResult error")
            #return result
            #return "\n<h2>some other result</h2>\n"

    form = {}
    config = {}

    result = '<html>\n'

    result += getStyle('blue')

    # all the following return HTML)
    result += '<h2>Dropdowns</h2><table border="1">'
    #result += handleResult(getAppOptions('pahma'),'getAppOptions')
    result += handleResult(getAltNumTypes(form, 'test-csid', 'attributed pahma number'),'getAltNumTypes')
    result += handleResult(getHandlers(form,'bampfa'),'getHandlers: bampfa')
    result += handleResult(getHandlers(form,''),'getHandlers')
    result += handleResult(getReasons(form,'bampfa'),'getReasons:bampfa')
    result += handleResult(getReasons(form,''),'getReasons')
    result += handleResult(getPrinters(form),'getPrinters')
    result += handleResult(getFieldset(form,'pahma'),'getFieldset')
    result += handleResult(getFieldset(form,'bampfa'),'getFieldset')
    result += handleResult(getHierarchies(form, ['']),'getHierarchies')
    result += handleResult(getAgencies(form),'getAgencies')
    result += '</table>'

    # these two return python objects
    result += '<h2>Tricoder users</h2><table border="1">'
    t = tricoderUsers()
    for k in t.keys():
        result += '<tr><td>%s</td><td>%s</td></tr>' % (k, t[k])
    result += '</table>'
    #result += '<h2>Prohibited Locations</h2>'
    #for p in getProhibitedLocations(config, request):
    #    result += '<li>%s</li>' % p

    result += '<h2>Headers</h2>'
    for h in 'inventory movecrate packinglist packinglistbyculture moveobject bedlist bedlistnone keyinfoResult objinfoResult inventoryResult barcodeprint barcodeprintlocations upload'.split(' '):
        result += '<h3>Header for %s</h3>' % h
        header = getHeader(h,'')
        result += header.replace('<table', '<table border="1" ')
        result += '</table>'

    result += '<h2>KIR/OIR/BOE Fieldset Headers</h2>'
    for h in 'keyinfo namedesc hsrinfo objtypecm registration dates places mattax'.split(' '):
        result += '<h3>Header for %s</h3>' % h
        header = infoHeaders(h)
        result += header.replace('<table', '<table border="1" ')
        result += '</table>'

    print('''Content-Type: text/html; charset=utf-8

    ''')
    print(result)


    result += '</html>\n'

