#!/usr/bin/env /usr/bin/python

import time
import sys
import cgi
import psycopg2

# reload(sys)
# sys.setdefaultencoding('utf-8')

# timeoutcommand = "set statement_timeout to 9000; SET NAMES 'utf8';"
timeoutcommand = "set statement_timeout to 1200000; SET NAMES 'utf8';"

def setupcursor(config, command):
    try:
        dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    except psycopg2.DatabaseError as e:
        sys.stderr.write('DB connection error: %s' % e)
        raise
        # return '%s' % e
    objects = dbconn.cursor()
    objects.execute(timeoutcommand)
    try:
        objects.execute(command)
    except psycopg2.DatabaseError as e:
        sys.stderr.write('DB query error: %s' % e)
        raise
    return objects

def testDB(config):
    dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    objects = dbconn.cursor()
    try:
        objects.execute('set statement_timeout to 5000')
        objects.execute('select * from hierarchy limit 30000')
        return "OK"
    except psycopg2.DatabaseError as e:
        sys.stderr.write('testDB error: %s' % e)
        return '%s' % e
    except:
        sys.stderr.write("some other testDB error!")
        return "Some other failure"


def dbtransaction(command, config):
    dbconn = psycopg2.connect(config.get('connect', 'connect_string'))
    cursor = dbconn.cursor()
    cursor.execute(command)


def setquery(type, location, qualifier, institution):

    if type == 'inventory':

        if institution == 'bampfa':
            return """
            SELECT distinct on (locationkey,objectnumber,h3.name)
(case when cb.computedcrate is Null then l.termdisplayName
     else concat(l.termdisplayName,
     ': ',regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
replace(concat(l.termdisplayName,
     ': ',regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1')),' ','0') AS locationkey,
m.locationdate,
cc.objectnumber objectnumber,
cc.numberofobjects objectCount,
tg.bampfatitle,
rc.subjectcsid movementCsid,
lc.refname movementRefname,
rc.subjectcsid  objectCsid,
''  objectRefname,
m.id moveid,
rc.subjectdocumenttype,
rc.objectdocumenttype,
cc.objectnumber sortableobjectnumber,
cb.computedcrate crateRefname,
regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1') crate,
regexp_replace(pg.bampfaobjectproductionperson, '^.*\\)''(.*)''$', '\\1') AS Artist

FROM loctermgroup l

join hierarchy h1 on l.id = h1.id
join locations_common lc on lc.id = h1.parentid
join movements_common m on m.currentlocation = lc.refname

join hierarchy h2 on m.id = h2.id
join relations_common rc on rc.objectcsid = h2.name

join hierarchy h3 on rc.subjectcsid = h3.name
join collectionobjects_common cc on (h3.id = cc.id and cc.computedcurrentlocation = lc.refname)

left outer join collectionobjects_bampfa cb on (cb.id=cc.id)

LEFT OUTER JOIN hierarchy h4 ON (h4.parentid = cc.id AND h4.name = 'collectionobjects_bampfa:bampfaTitleGroupList' and h4.pos=0)
LEFT OUTER JOIN bampfatitlegroup tg ON (h4.id = tg.id)

left outer join hierarchy h5 ON (cc.id = h5.parentid AND h5.name = 'collectionobjects_bampfa:bampfaObjectProductionPersonGroupList' AND (h5.pos = 0 OR h5.pos IS NULL))
left outer join bampfaobjectproductionpersongroup pg ON (h5.id = pg.id)

join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')

WHERE
   l.termdisplayName = '""" + str(location) + """'

ORDER BY locationkey,objectnumber asc

            """

        # else:

        return """
SELECT distinct on (locationkey,sortableobjectnumber,h3.name)
(case when ca.computedcrate is Null then l.termdisplayName  
     else concat(l.termdisplayName,
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
replace(concat(l.termdisplayName,
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')),' ','0') AS locationkey,
m.locationdate,
cc.objectnumber objectnumber,
cc.numberofobjects objectCount,
(case when ong.objectName is NULL then '' else regexp_replace(ong.objectName, '^.*\\)''(.*)''$', '\\1') end) objectName,
rc.subjectcsid movementCsid,
lc.refname movementRefname,
rc.objectcsid  objectCsid,
''  objectRefname,
m.id moveid,
rc.subjectdocumenttype,
rc.objectdocumenttype,
cp.sortableobjectnumber sortableobjectnumber,
ca.computedcrate crateRefname,
regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1') crate

FROM loctermgroup l

join hierarchy h1 on l.id = h1.id
join locations_common lc on lc.id = h1.parentid
join movements_common m on m.currentlocation = lc.refname

join hierarchy h2 on m.id = h2.id
join relations_common rc on rc.subjectcsid = h2.name

join hierarchy h3 on rc.objectcsid = h3.name
join collectionobjects_common cc on (h3.id = cc.id and cc.computedcurrentlocation = lc.refname)

left outer join collectionobjects_anthropology ca on (ca.id=cc.id)
left outer join hierarchy h5 on (cc.id = h5.parentid and h5.name = 'collectionobjects_common:objectNameList' and h5.pos=0)
left outer join objectnamegroup ong on (ong.id=h5.id)

left outer join collectionobjects_pahma cp on (cp.id=cc.id)

join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')

WHERE 
   l.termdisplayName = '""" + str(location) + """'
   
ORDER BY locationkey,sortableobjectnumber,h3.name desc
LIMIT 30000"""

    elif type == 'bedlist' or type == 'locreport':

        if type == 'bedlist':
            sortkey = 'gardenlocation'
            searchkey = 'lct.termdisplayname'
        elif type == 'locreport':
            sortkey = 'determination'
            searchkey = 'tig.taxon'

        queryTemplate = """
select distinct on (to_number(objectnumber,'9999.9999'))
case when (mc.currentlocation is not null and mc.currentlocation <> '') then regexp_replace(mc.currentlocation, '^.*\\)''(.*)''$', '\\1') end as gardenlocation,
lct.termname shortgardenlocation,
case when (lc.locationtype is not null and lc.locationtype <> '') then regexp_replace(lc.locationtype, '^.*\\)''(.*)''$', '\\1') end as locationtype,
co1.recordstatus,
co1.objectnumber,
findhybridaffinname(tig.id) as determination,
case when (tn.family is not null and tn.family <> '') then regexp_replace(tn.family, '^.*\\)''(.*)''$', '\\1') end as family,
h1.name as objectcsid,
con.rare,
cob.deadflag,
case when (tn.family is not null and tn.family <> '') then regexp_replace(tn.family, '^.*\\)''(.*)''$', '\\1') end as family,
date(mc.locationdate + interval '8 hours') actiondate,
regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') actionreason,
case when (mb.previouslocation is not null and mb.previouslocation <> '') then regexp_replace(mb.previouslocation, '^.*\\)''(.*)''$', '\\1') end as previouslocation,
array_to_string(array
      (SELECT
      CASE WHEN (tig3.taxon IS NOT NULL AND tig3.taxon <>'' and tig3.taxon not like '%no name%') THEN getdispl(tig3.taxon) ELSE '' END
       from collectionobjects_common co2
        inner join hierarchy h2int on co2.id = h2int.id
        left outer join hierarchy htig3 on (co2.id = htig3.parentid
        and htig3.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
        left outer join taxonomicIdentGroup tig3 on (tig3.id = htig3.id)
       where h2int.name=h1.name order by htig3.pos), '|', '') alldeterminations_ss
from collectionobjects_common co1 
join hierarchy h1 on co1.id=h1.id
left outer 
join hierarchy htig on (co1.id = htig.parentid and htig.pos = 0 and htig.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
left outer 
join taxonomicIdentGroup tig on (tig.id = htig.id)
left outer 
join taxon_common tc on (tig.taxon=tc.refname)
left outer 
join taxon_naturalhistory tn on (tc.id=tn.id) 
join relations_common r1 on (h1.name=r1.subjectcsid and objectdocumenttype='Movement') 
join hierarchy h2 on (r1.objectcsid=h2.name and h2.isversion is %s true) 
join movements_common mc on (mc.id=h2.id) 
join movements_botgarden mb on (mc.id=mb.id)
left outer
join loctermgroup lct on (regexp_replace(mc.currentlocation, '^.*\\)''(.*)''$', '\\1')=lct.termdisplayname)
%s
join collectionspace_core core on mc.id=core.id 
join collectionobjects_botgarden cob on (co1.id=cob.id) 
join collectionobjects_naturalhistory con on (co1.id = con.id)

left outer join locations_common lc on (mc.currentlocation=lc.refname) 
where %s  %s = '%s'
ORDER BY to_number(objectnumber,'9999.9999')
LIMIT 6000"""
            
        if qualifier == 'alive':
            queryPart1 = " regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') != 'Dead' and "
            queryPart2 = """join misc misc1 on (misc1.id = mc.id and misc1.lifecyclestate <> 'deleted') -- movement not deleted
                            join misc ms on (co1.id=ms.id and ms.lifecyclestate <> 'deleted')"""
            return queryTemplate % ('not', queryPart2, queryPart1, searchkey, location)
        elif qualifier == 'dead':
            queryPart1 = " regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') = 'Dead' and "
            queryPart2 = "inner join misc misc1 on (misc1.id = mc.id and misc1.lifecyclestate <> 'deleted') -- movement not deleted"
            return queryTemplate % ('', queryPart2, queryPart1, searchkey, location)
        else:
            raise
            # houston, we got a problem...query not qualified

    elif type == 'keyinfo' or type == 'barcodeprint' or type == 'packinglist':

        if institution == 'bampfa':
            return """
            SELECT distinct on (location,objectnumber)
(case when cb.computedcrate is Null then l.termdisplayName
     else concat(l.termdisplayName,
     ': ',regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS location,
cc.objectnumber AS objectnumber,
h3.name,
tg.bampfatitle AS Title,
regexp_replace(pg.bampfaobjectproductionperson, '^.*\\)''(.*)''$', '\\1') AS Artist,
regexp_replace(pg.bampfaobjectproductionpersonrole, '^.*\\)''(.*)''$', '\\1') AS ArtistRole,
cc.physicalDescription AS Medium,
mp.dimensionsummary AS measurement,
regexp_replace(bcl.item, '^.*\\)''(.*)''$', '\\1') AS Collection,
cb.creditline AS CreditLine,
cb.legalstatus AS LegalStatus,
'dd MM YYYY' AS AcqDate,
case when (bd.item is not null and bd.item <> '') then bd.item end AS briefdescription,
m.movementnote,
cb.accNumberPrefix,
cb.accNumberPart1 ,
cb.accNumberPart2,
cb.accNumberPart3,
cb.accNumberPart4 ,
cb.accNumberPart5 ,
pg.bampfaobjectproductionperson AS Artistrefname,
pg.bampfaobjectproductionpersonrole AS ArtistRolerefname,
bcl.item

FROM loctermgroup l

join hierarchy h1 on l.id = h1.id
join locations_common lc on lc.id = h1.parentid
join movements_common m on m.currentlocation = lc.refname

join hierarchy h2 on m.id = h2.id
join relations_common rc on rc.objectcsid = h2.name

join hierarchy h3 on rc.subjectcsid = h3.name

join collectionobjects_common cc on (h3.id = cc.id and cc.computedcurrentlocation = lc.refname)
join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')
left outer join collectionobjects_bampfa cb on (cb.id=cc.id)
left outer join collectionobjects_bampfa_bampfacollectionlist bcl on (bcl.id=cb.id)

LEFT OUTER JOIN hierarchy h4 ON (h4.parentid = cc.id AND h4.name = 'collectionobjects_bampfa:bampfaTitleGroupList' and h4.pos=0)
LEFT OUTER JOIN bampfatitlegroup tg ON (h4.id = tg.id)

left outer join hierarchy h5 ON (cc.id = h5.parentid AND h5.name = 'collectionobjects_bampfa:bampfaObjectProductionPersonGroupList' AND (h5.pos = 0 OR h5.pos IS NULL))
left outer join bampfaobjectproductionpersongroup pg ON (h5.id = pg.id)

left outer join hierarchy h7 ON (h7.parentid = cc.id AND h7.name = 'collectionobjects_common:measuredPartGroupList' and h7.pos=0)
left outer join measuredpartgroup mp ON (h7.id = mp.id)

join collectionobjects_common_briefdescriptions bd on (bd.id=cc.id and bd.pos=0)

WHERE
   l.termdisplayName = '""" + str(location) + """'


ORDER BY location,objectnumber asc
LIMIT 30000
            """

        else:

            return """
SELECT distinct on (locationkey,sortableobjectnumber,h3.name)
(case when ca.computedcrate is Null then l.termdisplayName  
     else concat(l.termdisplayName,
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
replace(concat(l.termdisplayName,
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')),' ','0') AS locationkey,
m.locationdate,
cc.objectnumber objectnumber,
(case when ong.objectName is NULL then '' else regexp_replace(ong.objectName, '^.*\\)''(.*)''$', '\\1') end) objectName,
cc.numberofobjects objectCount,
case when (pfc.item is not null and pfc.item <> '') then
substring(pfc.item, position(')''' IN pfc.item)+2, LENGTH(pfc.item)-position(')''' IN pfc.item)-2)
end AS fieldcollectionplace,
case when (apg.assocpeople is not null and apg.assocpeople <> '') then
substring(apg.assocpeople, position(')''' IN apg.assocpeople)+2, LENGTH(apg.assocpeople)-position(')''' IN apg.assocpeople)-2)
end as culturalgroup,
rc.objectcsid  objectCsid,
case when (pef.item is not null and pef.item <> '') then
substring(pef.item, position(')''' IN pef.item)+2, LENGTH(pef.item)-position(')''' IN pef.item)-2)
end as ethnographicfilecode,
pfc.item fcpRefName,
apg.assocpeople cgRefName,
pef.item efcRefName,
ca.computedcrate,
regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1') crate,
case when (bd.item is not null and bd.item <> '') then
bd.item end as briefdescription,
case when (pc.item is not null and pc.item <> '') then
substring(pc.item, position(')''' IN pc.item)+2, LENGTH(pc.item)-position(')''' IN pc.item)-2)
end as fieldcollector,
case when (donor.item is not null and donor.item <> '') then
substring(donor.item, position(')''' IN donor.item)+2, LENGTH(donor.item)-position(')''' IN donor.item)-2)
end as donor,
case when (an.pahmaaltnum is not null and an.pahmaaltnum <> '') then
an.pahmaaltnum end as altnum,
case when (an.pahmaaltnumtype is not null and an.pahmaaltnumtype <> '') then
an.pahmaaltnumtype end as altnumtype,
pc.item pcRefName,
ac.acquisitionreferencenumber accNum,
donor.item pdRefName,
ac.id accID,
h9.name accCSID,
cp.inventoryCount,
cc.collection,
rd.item responsibledepartment,
cp.pahmafieldlocverbatim,
fcd.datedisplaydate fcdate,
REGEXP_REPLACE(matg.material, '^.*\\)''(.*)''$', '\\1') material,
REGEXP_REPLACE(opp.objectProductionPlace, '^.*\\)''(.*)''$', '\\1') productionplace,
pd.datedisplaydate productiondate,
REGEXP_REPLACE(tig.taxon, '^.*\\)''(.*)''$', '\\1') taxon,
ddep.datedisplaydate contentDateGroup,
REGEXP_REPLACE(conp.item, '^.*\\)''(.*)''$', '\\1') contentPlace,
REGEXP_REPLACE(ope.objectProductionPerson, '^.*\\)''(.*)''$', '\\1') productionperson,
pobs.item objectstatus

FROM loctermgroup l

join hierarchy h1 on l.id = h1.id
join locations_common lc on lc.id = h1.parentid
join movements_common m on m.currentlocation = lc.refname

join hierarchy h2 on m.id = h2.id
join relations_common rc on rc.subjectcsid = h2.name

join hierarchy h3 on rc.objectcsid = h3.name
join collectionobjects_common cc on (h3.id = cc.id and cc.computedcurrentlocation = lc.refname)

left outer join hierarchy h4 on (cc.id = h4.parentid and h4.name = 'collectionobjects_common:objectNameList' and (h4.pos=0 or h4.pos is null))
left outer join objectnamegroup ong on (ong.id=h4.id)

left outer join collectionobjects_anthropology ca on (ca.id=cc.id)
left outer join collectionobjects_pahma cp on (cp.id=cc.id)
left outer join collectionobjects_pahma_pahmafieldcollectionplacelist pfc on (pfc.id=cc.id and (pfc.pos=0 or pfc.pos is null))
left outer join collectionobjects_pahma_pahmaethnographicfilecodelist pef on (pef.id=cc.id and (pef.pos=0 or pef.pos is null))
left outer join collectionobjects_pahma_pahmaobjectstatuslist pobs ON (pobs.id = cc.id and pobs.pos=0)

left outer join hierarchy h5 on (cc.id=h5.parentid and h5.primarytype = 'assocPeopleGroup' and (h5.pos=0 or h5.pos is null))
left outer join assocpeoplegroup apg on (apg.id=h5.id)
 
left outer join collectionobjects_common_briefdescriptions bd on (bd.id=cc.id and bd.pos=0)
left outer join collectionobjects_common_contentplaces conp on (conp.id=cc.id and conp.pos=0)
left outer join collectionobjects_common_fieldcollectors pc on (pc.id=cc.id and pc.pos=0)

FULL OUTER JOIN relations_common rc6 ON (rc6.subjectcsid = h1.name AND rc6.objectdocumenttype = 'Acquisition')
FULL OUTER JOIN hierarchy h7 ON (h7.name = rc6.objectcsid)
FULL OUTER JOIN acquisitions_common ac ON (ac.id = h7.id)
FULL OUTER JOIN hierarchy h9 ON (ac.id = h9.id)
FULL OUTER JOIN acquisitions_common_owners donor ON (ac.id = donor.id AND (donor.pos = 0 OR donor.pos IS NULL))
FULL OUTER JOIN misc msac ON (ac.id = msac.id AND msac.lifecyclestate <> 'deleted')

FULL OUTER JOIN hierarchy h8 ON (cc.id = h8.parentid AND h8.name = 'collectionobjects_pahma:pahmaAltNumGroupList' AND (h8.pos = 0 OR h8.pos IS NULL))
FULL OUTER JOIN pahmaaltnumgroup an ON (h8.id = an.id)

FULL OUTER JOIN hierarchy h10 ON (h10.parentid = cc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_pahma:pahmaFieldCollectionDateGroupList')
FULL OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)

FULL OUTER JOIN hierarchy h11 ON (cc.id=h11.parentid AND h11.name='collectionobjects_common:objectProductionPlaceGroupList' AND (h11.pos=0 OR h11.pos IS NULL))
FULL OUTER JOIN objectproductionplacegroup opp ON (h11.id=opp.id)

FULL OUTER JOIN hierarchy h12 ON (h12.parentid = cc.id AND h12.name = 'collectionobjects_common:objectProductionDateGroupList'  AND (h12.pos=0 OR h12.pos IS NULL))
FULL OUTER JOIN structureddategroup pd ON (pd.id = h12.id)

FULL OUTER JOIN hierarchy h13 ON (h13.parentid = cc.id AND h13.name='collectionobjects_common:materialGroupList' AND (h13.pos=0 OR h13.pos IS NULL))
FULL OUTER JOIN materialgroup matg ON (h13.id = matg.id)

FULL OUTER JOIN hierarchy htig on (cc.id = htig.parentid AND htig.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList' AND (htig.pos=0 OR htig.pos IS NULL))
FULL OUTER JOIN taxonomicIdentGroup tig ON (tig.id = htig.id)

FULL OUTER JOIN hierarchy h14 ON (h14.parentid = cc.id AND h14.name = 'collectionobjects_common:contentDateGroup'  AND (h14.pos=0 OR h14.pos IS NULL))
FULL OUTER JOIN structureddategroup ddep ON (ddep.id = h14.id)

FULL OUTER JOIN hierarchy h15 ON (cc.id=h15.parentid AND h15.name='collectionobjects_common:objectProductionPersonGroupList' AND (h15.pos=0 OR h15.pos IS NULL))
FULL OUTER JOIN objectproductionpersongroup ope ON (h15.id=ope.id)

left outer join collectionobjects_common_responsibledepartments rd on (rd.id=cc.id and rd.pos=0)

join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')

WHERE 
   l.termdisplayName = '""" + str(location) + """'

   
ORDER BY locationkey,sortableobjectnumber,h3.name desc
LIMIT 30000
"""

    elif type == 'getalltaxa':
        queryTemplate = """
select co1.objectnumber,
findhybridaffinname(tig.id) as determination,
case when (tn.family is not null and tn.family <> '')
     then regexp_replace(tn.family, '^.*\\)''(.*)''$', '\\1')
end as family,
case when (mc.currentlocation is not null and mc.currentlocation <> '')
     then regexp_replace(mc.currentlocation, '^.*\\)''(.*)''$', '\\1')
end as gardenlocation,
co1.recordstatus dataQuality,
case when (lg.fieldlocplace is not null and lg.fieldlocplace <> '') then regexp_replace(lg.fieldlocplace, '^.*\\)''(.*)''$', '\\1')
     when (lg.fieldlocplace is null and lg.taxonomicrange is not null) then 'Geographic range: '||lg.taxonomicrange
end as locality,
h1.name as objectcsid,
con.rare,
cob.deadflag,
regexp_replace(tig2.taxon, '^.*\\)''(.*)''$', '\\1') as determinationNoAuth,
regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1'),
case when (tn.family is not null and tn.family <> '') then regexp_replace(tn.family, '^.*\\)''(.*)''$', '\\1') end as family,
date(mc.locationdate + interval '8 hours') actiondate,
case when (mb.previouslocation is not null and mb.previouslocation <> '') then regexp_replace(mb.previouslocation, '^.*\\)''(.*)''$', '\\1') end as previouslocation,
array_to_string(array
      (SELECT
      CASE WHEN (tig3.taxon IS NOT NULL AND tig3.taxon <>'' and tig3.taxon not like '%no name%') THEN getdispl(tig3.taxon) ELSE '' END
       from collectionobjects_common co2
        inner join hierarchy h2int on co2.id = h2int.id
        left outer join hierarchy htig3 on (co2.id = htig3.parentid
        and htig3.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
        left outer join taxonomicIdentGroup tig3 on (tig3.id = htig3.id)
       where h2int.name=h1.name order by htig3.pos), '|', '') alldeterminations_ss

from collectionobjects_common co1

join hierarchy h1 on co1.id=h1.id
join relations_common r1 on (h1.name=r1.subjectcsid and objectdocumenttype='Movement')
join hierarchy h2 on (r1.objectcsid=h2.name and h2.isversion is not true)
join movements_common mc on (mc.id=h2.id %s)
join movements_botgarden mb on (mc.id=mb.id)
%s

join collectionobjects_naturalhistory con on (co1.id = con.id)
join collectionobjects_botgarden cob on (co1.id=cob.id)

left outer join hierarchy htig
     on (co1.id = htig.parentid and htig.pos = 0 and htig.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
left outer join taxonomicIdentGroup tig on (tig.id = htig.id)

left outer join hierarchy htig2
     on (co1.id = htig2.parentid and htig2.pos = 1 and htig2.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
left outer join taxonomicIdentGroup tig2 on (tig2.id = htig2.id)

left outer join hierarchy hlg
     on (co1.id = hlg.parentid and hlg.pos = 0 and hlg.name='collectionobjects_naturalhistory:localityGroupList')
left outer join localitygroup lg on (lg.id = hlg.id)

join collectionspace_core core on (core.id=co1.id and core.tenantid=35)
join misc misc2 on (misc2.id = co1.id and misc2.lifecyclestate <> 'deleted') -- object not deleted

left outer join taxon_common tc on (tig.taxon=tc.refname)
left outer join taxon_naturalhistory tn on (tc.id=tn.id) """
        # the form of the query for finding Deads and Alives is a bit different, so we
        # need to build the query string based on what we are trying to make a list of...deads or alives.
        sys.stderr.write('qualifier %s' % qualifier)
        if qualifier == 'alive':
            queryPart1 = ""
            queryPart2 = "join misc misc1 on (misc1.id = mc.id and misc1.lifecyclestate <> 'deleted') -- movement not deleted"
            return queryTemplate % (queryPart1, queryPart2)
        elif qualifier == 'dead':
            queryPart1 = " and regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') = 'Dead'"
            queryPart2 = " "
            return queryTemplate % (queryPart1, queryPart2)
        elif qualifier == 'dead or alive':
            queryPart1 = ""
            queryPart2 = "join misc misc1 on (misc1.id = mc.id and misc1.lifecyclestate <> 'deleted') -- movement not deleted"
            part1 = queryTemplate % (queryPart1, queryPart2)
            queryPart1 = " and regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') = 'Dead'"
            queryPart2 = " "
            part2 = queryTemplate % (queryPart1, queryPart2)
            return part1 + ' UNION ' + part2
        else:
            raise
            # houston, we got a problem...query not qualified



# regexp_replace(mc.reasonformove, '^.*\\)''(.*)''$', '\\1') = 'Dead'.
#left outer join taxon_naturalhistory tn on (tc.id=tn.id)""" % ("and con.rare = 'true'","and cob.deadflag = 'false'")

def getlocations(location1, location2, num2ret, config, updateType, institution):

    debug = False

    result = []

    for loc in getloclist('set', location1, '', num2ret, config):
        getobjects = setquery(updateType, loc[0], '', institution)

        try:
            elapsedtime = time.time()
            objects = setupcursor(config, getobjects)
            elapsedtime = time.time() - elapsedtime
            if debug: sys.stderr.write('all objects: %s :: %s\n' % (loc[0], elapsedtime))
        except psycopg2.DatabaseError as e:
            sys.stderr.write('getlocations select error: %s' % e)
            #return result
            raise
        except:
            sys.stderr.write("some other getlocations database error!")
            #return result
            raise

        try:
            rows = [list(item) for item in objects.fetchall()]
        except psycopg2.DatabaseError as e:
            sys.stderr.write("fetchall getlocations database error!")

        if debug: sys.stderr.write('number objects to be checked: %s\n' % len(rows))
        try:
            for row in rows:
                result.append(row)
        except:
            sys.stderr.write("other getobjects error: %s" % len(rows))
            raise

    return result


def getplants(location1, location2, num2ret, config, updateType, qualifier):

    debug = False

    result = []

    #for loc in getloclist('set',location1,'',num2ret,config):
    getobjects = setquery(updateType, location1, qualifier, 'ucbg')
    #print("<span>%s</span>" % getobjects)
    try:
        elapsedtime = time.time()
        objects = setupcursor(config, getobjects)
        elapsedtime = time.time() - elapsedtime
        #sys.stderr.write('query :: %s\n' % getobjects)
        if debug: sys.stderr.write('all objects: %s :: %s\n' % (location1, elapsedtime))
    except psycopg2.DatabaseError as e:
        raise
        #sys.stderr.write('getplants select error: %s' % e)
        #return result
    except:
        sys.stderr.write("some other getplants database error!")
        return result

    try:
        result = [list(item) for item in objects.fetchall()]
        if debug: sys.stderr.write('object count: %s\n' % (len(result)))
    except psycopg2.DatabaseError as e:
        sys.stderr.write("fetchall getplants database error!")

    return result

def getgrouplist(group, num2ret, config):
    if int(num2ret) > 30000: num2ret = 30000
    if int(num2ret) < 1:    num2ret = 1
    institution = config.get('info', 'institution')

    if institution == 'bampfa':
        getobjects = """
                    SELECT distinct on (storageLocation,objectnumber,hx2.name)
(case when cb.computedcrate is Null then regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1')
     else concat(regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1'),
     ': ',regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
        cc.computedcurrentlocation AS locrefname,
        '' as locationdate,
        cc.objectnumber objectnumber,
        tg.bampfatitle,
        cc.numberofobjects objectCount,
        '' as movementCsid,
        '' as movementRefname,
        hx2.name as objectCsid,
        ''  objectRefname,
        '' as moveid,
        '' as subjectdocumenttype,
        '' as objectdocumenttype,
        cc.objectnumber sortableobjectnumber,
        cb.computedcrate crateRefname,
        regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1') crate,
        regexp_replace(pg.bampfaobjectproductionperson, '^.*\\)''(.*)''$', '\\1') AS Artist

        FROM groups_common gc
        JOIN misc mc1 ON (gc.id = mc1.id AND mc1.lifecyclestate <> 'deleted')

        JOIN hierarchy h1 ON (gc.id=h1.id)
        JOIN relations_common rc1 ON (h1.name=rc1.subjectcsid)
        JOIN hierarchy hx2 ON (rc1.objectcsid=hx2.name)
        JOIN collectionobjects_common cc ON (hx2.id=cc.id)

        left outer join collectionobjects_bampfa cb on (cb.id=cc.id)

        LEFT OUTER JOIN hierarchy h4 ON (h4.parentid = cc.id AND h4.name = 'collectionobjects_bampfa:bampfaTitleGroupList' and h4.pos=0)
        LEFT OUTER JOIN bampfatitlegroup tg ON (h4.id = tg.id)

        left outer join hierarchy h5 ON (cc.id = h5.parentid AND h5.name = 'collectionobjects_bampfa:bampfaObjectProductionPersonGroupList' AND (h5.pos = 0 OR h5.pos IS NULL))
        left outer join bampfaobjectproductionpersongroup pg ON (h5.id = pg.id)

        WHERE
        gc.title='""" + group + """'
        ORDER BY storageLocation,objectnumber,hx2.name asc
        limit """ + str(num2ret)

    else:
        getobjects = """SELECT DISTINCT ON (sortableobjectnumber)
(case when ca.computedcrate is Null then regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1')
     else concat(regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1'),
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
cc.computedcurrentlocation AS locrefname,
'' AS locdate,
cc.objectnumber objectnumber,
(case when ong.objectName is NULL then '' else regexp_replace(ong.objectName, '^.*\\)''(.*)''$', '\\1') end) objectName,
cc.numberofobjects objectCount,
case when (pfc.item is not null and pfc.item <> '') then
 substring(pfc.item, position(')''' IN pfc.item)+2, LENGTH(pfc.item)-position(')''' IN pfc.item)-2)
end AS fieldcollectionplace,
case when (apg.assocpeople is not null and apg.assocpeople <> '') then
 substring(apg.assocpeople, position(')''' IN apg.assocpeople)+2, LENGTH(apg.assocpeople)-position(')''' IN apg.assocpeople)-2)
end as culturalgroup,
hx2.name AS csid,
case when (pef.item is not null and pef.item <> '') then
 substring(pef.item, position(')''' IN pef.item)+2, LENGTH(pef.item)-position(')''' IN pef.item)-2)
end as ethnographicfilecode,
pfc.item fcpRefName,
apg.assocpeople cgRefName,
pef.item efcRefName,
ca.computedcrate crateRefname,
regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1') crate,
case when (bd.item is not null and bd.item <> '') then
bd.item end as briefdescription,
case when (pc.item is not null and pc.item <> '') then
substring(pc.item, position(')''' IN pc.item)+2, LENGTH(pc.item)-position(')''' IN pc.item)-2)
end as fieldcollector,
case when (donor.item is not null and donor.item <> '') then
substring(donor.item, position(')''' IN donor.item)+2, LENGTH(donor.item)-position(')''' IN donor.item)-2)
end as donor,
case when (an.pahmaaltnum is not null and an.pahmaaltnum <> '') then
an.pahmaaltnum end as altnum,
case when (an.pahmaaltnumtype is not null and an.pahmaaltnumtype <> '') then
an.pahmaaltnumtype end as altnumtype,
pc.item pcRefName,
ac.acquisitionreferencenumber accNum,
donor.item pdRefName,
ac.id accID,
h9.name accCSID,
cp.inventoryCount,
cc.collection,
rd.item,
cp.pahmafieldlocverbatim,
fcd.datedisplaydate fcdate,
REGEXP_REPLACE(matg.material, '^.*\\)''(.*)''$', '\\1') material,
REGEXP_REPLACE(opp.objectProductionPlace, '^.*\\)''(.*)''$', '\\1') productionplace,
pd.datedisplaydate productiondate,
REGEXP_REPLACE(tig.taxon, '^.*\\)''(.*)''$', '\\1') taxon,
ddep.datedisplaydate contentDateGroup,
REGEXP_REPLACE(conp.item, '^.*\\)''(.*)''$', '\\1') contentPlace,
REGEXP_REPLACE(ope.objectProductionPerson, '^.*\\)''(.*)''$', '\\1') productionperson,
pobs.item objectstatus

FROM groups_common gc

JOIN misc mc1 ON (gc.id = mc1.id AND mc1.lifecyclestate <> 'deleted')
JOIN hierarchy h1 ON (gc.id=h1.id)
JOIN relations_common rc1 ON (h1.name=rc1.subjectcsid)
JOIN hierarchy hx2 ON (rc1.objectcsid=hx2.name)
JOIN collectionobjects_common cc ON (hx2.id=cc.id)
JOIN collectionobjects_pahma cp on(cp.id = cc.id)

left outer join hierarchy h4 on (cc.id = h4.parentid and h4.name = 'collectionobjects_common:objectNameList' and (h4.pos=0 or h4.pos is null))
left outer join objectnamegroup ong on (ong.id=h4.id)

left outer join collectionobjects_anthropology ca on (ca.id=cc.id)
left outer join collectionobjects_pahma_pahmafieldcollectionplacelist pfc on (pfc.id=cc.id and pfc.pos=0)
left outer join collectionobjects_pahma_pahmaethnographicfilecodelist pef on (pef.id=cc.id and pef.pos=0)
left outer join collectionobjects_pahma_pahmaobjectstatuslist pobs ON (pobs.id = cc.id and pobs.pos=0)

left outer join hierarchy h5 on (cc.id=h5.parentid and h5.primarytype = 'assocPeopleGroup' and (h5.pos=0 or h5.pos is null))
left outer join assocpeoplegroup apg on (apg.id=h5.id)

left outer join collectionobjects_common_briefdescriptions bd on (bd.id=cc.id and bd.pos=0)
left outer join collectionobjects_common_contentplaces conp on (conp.id=cc.id and conp.pos=0)
left outer join collectionobjects_common_fieldcollectors pc on (pc.id=cc.id and pc.pos=0)

FULL OUTER JOIN relations_common rc6 ON (rc6.subjectcsid = hx2.name AND rc6.objectdocumenttype = 'Acquisition')
FULL OUTER JOIN hierarchy h7 ON (h7.name = rc6.objectcsid)
FULL OUTER JOIN acquisitions_common ac ON (ac.id = h7.id)
FULL OUTER JOIN hierarchy h9 ON (ac.id = h9.id)
FULL OUTER JOIN acquisitions_common_owners donor ON (ac.id = donor.id AND (donor.pos = 0 OR donor.pos IS NULL))
FULL OUTER JOIN misc msac ON (ac.id = msac.id AND msac.lifecyclestate <> 'deleted')

FULL OUTER JOIN hierarchy h8 ON (cc.id = h8.parentid AND h8.name = 'collectionobjects_pahma:pahmaAltNumGroupList' AND (h8.pos = 0 OR h8.pos IS NULL))
FULL OUTER JOIN pahmaaltnumgroup an ON (h8.id = an.id)

FULL OUTER JOIN hierarchy h10 ON (h10.parentid = cc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_pahma:pahmaFieldCollectionDateGroupList')
FULL OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)

FULL OUTER JOIN hierarchy h11 ON (cc.id=h11.parentid AND h11.name='collectionobjects_common:objectProductionPlaceGroupList' AND (h11.pos=0 OR h11.pos IS NULL))
FULL OUTER JOIN objectproductionplacegroup opp ON (h11.id=opp.id)

FULL OUTER JOIN hierarchy h12 ON (h12.parentid = cc.id AND h12.name = 'collectionobjects_common:objectProductionDateGroupList'  AND (h12.pos=0 OR h12.pos IS NULL))
FULL OUTER JOIN structureddategroup pd ON (pd.id = h12.id)

FULL OUTER JOIN hierarchy h13 ON (h13.parentid = cc.id AND h13.name='collectionobjects_common:materialGroupList' AND (h13.pos=0 OR h13.pos IS NULL))
FULL OUTER JOIN materialgroup matg ON (h13.id = matg.id)

FULL OUTER JOIN hierarchy htig on (cc.id = htig.parentid AND htig.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList' AND (htig.pos=0 OR htig.pos IS NULL))
FULL OUTER JOIN taxonomicIdentGroup tig ON (tig.id = htig.id)

FULL OUTER JOIN hierarchy h14 ON (h14.parentid = cc.id AND h14.name = 'collectionobjects_common:contentDateGroup'  AND (h14.pos=0 OR h14.pos IS NULL))
FULL OUTER JOIN structureddategroup ddep ON (ddep.id = h14.id)

FULL OUTER JOIN hierarchy h15 ON (cc.id=h15.parentid AND h15.name='collectionobjects_common:objectProductionPersonGroupList' AND (h15.pos=0 OR h15.pos IS NULL))
FULL OUTER JOIN objectproductionpersongroup ope ON (h15.id=ope.id)

left outer join collectionobjects_common_responsibledepartments rd on (rd.id=cc.id and rd.pos=0)

join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')

WHERE
   gc.title='""" + group + """'
limit """ + str(num2ret)


    try:
        objects = setupcursor(config, getobjects)
        #for object in objects.fetchall():
        #print(object)
        return [list(item) for item in objects.fetchall()], ''
    except:
        return [], 'problem with group query'


def getloclist(searchType, location1, location2, num2ret, config):
    # 'set' means 'next num2ret locations', otherwise prefix match
    if searchType == 'set':
        whereclause = "WHERE locationkey >= replace('" + location1 + "',' ','0')"
    elif searchType == 'exact':
        whereclause = "WHERE locationkey = replace('" + location1 + "',' ','0')"
    elif searchType == 'prefix':
        whereclause = "WHERE locationkey LIKE replace('" + location1 + "%',' ','0')"
    elif searchType == 'range':
        whereclause = "WHERE locationkey >= replace('" + location1 + "',' ','0') AND locationkey <= replace('" + location2 + "',' ','0')"

    if int(num2ret) > 30000: num2ret = 30000
    if int(num2ret) < 1:    num2ret = 1

    getobjects = """
select * from (
select termdisplayname,replace(termdisplayname,' ','0') locationkey 
FROM loctermgroup ltg
INNER JOIN hierarchy h_ltg
        ON h_ltg.id=ltg.id
INNER JOIN hierarchy h_loc
        ON h_loc.id=h_ltg.parentid
INNER JOIN misc
        ON misc.id=h_loc.id and misc.lifecyclestate <> 'deleted'
) as t
""" + whereclause + """
order by locationkey
limit """ + str(num2ret)

    try:
        objects = setupcursor(config, getobjects)
        #for object in objects.fetchall():
        #print(object)
        # return objects.fetchall()
        return [list(item) for item in objects.fetchall()]
    except:
        raise


def getobjlist(searchType, object1, object2, num2ret, config):
    query1 = """
    SELECT objectNumber,
cp.sortableobjectnumber
FROM collectionobjects_common cc
left outer join collectionobjects_pahma cp on (cp.id=cc.id)
INNER JOIN hierarchy h1
        ON cc.id=h1.id
INNER JOIN misc
        ON misc.id=h1.id and misc.lifecyclestate <> 'deleted'
WHERE
     cc.objectNumber = '%s'"""

    if int(num2ret) > 1000: num2ret = 1000
    if int(num2ret) < 1:    num2ret = 1

    try:
        objects = setupcursor(config, query1 % object1)
        (object1, sortkey1) = objects.fetchone()
        objects = setupcursor(config, query1 % object2)
        (object2, sortkey2) = objects.fetchone()
    except:
        return [], 'problem'

    # 'set' means 'next num2ret objects', otherwise prefix match
    if searchType == 'set':
        whereclause = "WHERE sortableobjectnumber >= '" + sortkey1 + "'"
    elif searchType == 'prefix':
        whereclause = "WHERE sortableobjectnumber LIKE '" + sortkey1 + "%'"
    elif searchType == 'range':
        whereclause = "WHERE sortableobjectnumber >= '" + sortkey1 + "' AND sortableobjectnumber <= '" + sortkey2 + "'"

    getobjects = """SELECT DISTINCT ON (sortableobjectnumber)
(case when ca.computedcrate is Null then regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1') 
     else concat(regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1'),
     ': ',regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1')) end) AS storageLocation,
cc.computedcurrentlocation AS locrefname,
'' AS locdate,
cc.objectnumber objectnumber,
(case when ong.objectName is NULL then '' else regexp_replace(ong.objectName, '^.*\\)''(.*)''$', '\\1') end) objectName,
cc.numberofobjects objectCount,
case when (pfc.item is not null and pfc.item <> '') then
 substring(pfc.item, position(')''' IN pfc.item)+2, LENGTH(pfc.item)-position(')''' IN pfc.item)-2)
end AS fieldcollectionplace,
case when (apg.assocpeople is not null and apg.assocpeople <> '') then
 substring(apg.assocpeople, position(')''' IN apg.assocpeople)+2, LENGTH(apg.assocpeople)-position(')''' IN apg.assocpeople)-2)
end as culturalgroup,
h1.name  objectCsid,
case when (pef.item is not null and pef.item <> '') then
 substring(pef.item, position(')''' IN pef.item)+2, LENGTH(pef.item)-position(')''' IN pef.item)-2)
end as ethnographicfilecode,
pfc.item fcpRefName,
apg.assocpeople cgRefName,
pef.item efcRefName,
ca.computedcrate crateRefname,
regexp_replace(ca.computedcrate, '^.*\\)''(.*)''$', '\\1') crate,
case when (bd.item is not null and bd.item <> '') then
bd.item end as briefdescription,
case when (pc.item is not null and pc.item <> '') then
substring(pc.item, position(')''' IN pc.item)+2, LENGTH(pc.item)-position(')''' IN pc.item)-2)
end as fieldcollector,
case when (donor.item is not null and donor.item <> '') then
substring(donor.item, position(')''' IN donor.item)+2, LENGTH(donor.item)-position(')''' IN donor.item)-2)
end as donor,
case when (an.pahmaaltnum is not null and an.pahmaaltnum <> '') then
an.pahmaaltnum end as altnum,
case when (an.pahmaaltnumtype is not null and an.pahmaaltnumtype <> '') then
an.pahmaaltnumtype end as altnumtype,
pc.item pcRefName,
ac.acquisitionreferencenumber accNum,
donor.item pdRefName,
ac.id accID,
h9.name accCSID,
cp.inventoryCount,
cc.collection,
rd.item,
cp.pahmafieldlocverbatim,
fcd.datedisplaydate fcdate,
REGEXP_REPLACE(matg.material, '^.*\\)''(.*)''$', '\\1') material,
REGEXP_REPLACE(opp.objectProductionPlace, '^.*\\)''(.*)''$', '\\1') productionplace,
pd.datedisplaydate productiondate,
REGEXP_REPLACE(tig.taxon, '^.*\\)''(.*)''$', '\\1') taxon,
ddep.datedisplaydate contentDateGroup,
REGEXP_REPLACE(conp.item, '^.*\\)''(.*)''$', '\\1') contentPlace,
REGEXP_REPLACE(ope.objectProductionPerson, '^.*\\)''(.*)''$', '\\1') productionperson,
pobs.item objectstatus

FROM collectionobjects_pahma cp
left outer join collectionobjects_common cc on (cp.id=cc.id)

left outer join hierarchy h1 on (cp.id = h1.id)

left outer join hierarchy h4 on (cc.id = h4.parentid and h4.name = 'collectionobjects_common:objectNameList' and (h4.pos=0 or h4.pos is null))
left outer join objectnamegroup ong on (ong.id=h4.id)

left outer join collectionobjects_anthropology ca on (ca.id=cc.id)
left outer join collectionobjects_pahma_pahmafieldcollectionplacelist pfc on (pfc.id=cc.id and pfc.pos=0)
left outer join collectionobjects_pahma_pahmaethnographicfilecodelist pef on (pef.id=cc.id and pef.pos=0)
FULL OUTER JOIN collectionobjects_pahma_pahmaobjectstatuslist pobs ON (pobs.id = cc.id and pobs.pos=0)

left outer join hierarchy h5 on (cc.id=h5.parentid and h5.primarytype = 'assocPeopleGroup' and (h5.pos=0 or h5.pos is null))
left outer join assocpeoplegroup apg on (apg.id=h5.id)
 
left outer join collectionobjects_common_briefdescriptions bd on (bd.id=cc.id and bd.pos=0)
left outer join collectionobjects_common_contentplaces conp on (conp.id=cc.id and conp.pos=0)
left outer join collectionobjects_common_fieldcollectors pc on (pc.id=cc.id and pc.pos=0)

FULL OUTER JOIN relations_common rc6 ON (rc6.subjectcsid = h1.name AND rc6.objectdocumenttype = 'Acquisition')
FULL OUTER JOIN hierarchy h7 ON (h7.name = rc6.objectcsid)
FULL OUTER JOIN acquisitions_common ac ON (ac.id = h7.id)
FULL OUTER JOIN hierarchy h9 ON (ac.id = h9.id)
FULL OUTER JOIN acquisitions_common_owners donor ON (ac.id = donor.id AND (donor.pos = 0 OR donor.pos IS NULL))
FULL OUTER JOIN misc msac ON (ac.id = msac.id AND msac.lifecyclestate <> 'deleted')

FULL OUTER JOIN hierarchy h8 ON (cc.id = h8.parentid AND h8.name = 'collectionobjects_pahma:pahmaAltNumGroupList' AND (h8.pos = 0 OR h8.pos IS NULL))
FULL OUTER JOIN pahmaaltnumgroup an ON (h8.id = an.id)

FULL OUTER JOIN hierarchy h10 ON (h10.parentid = cc.id AND h10.pos = 0 AND h10.name = 'collectionobjects_pahma:pahmaFieldCollectionDateGroupList')
FULL OUTER JOIN structureddategroup fcd ON (fcd.id = h10.id)

FULL OUTER JOIN hierarchy h11 ON (cc.id=h11.parentid AND h11.name='collectionobjects_common:objectProductionPlaceGroupList' AND (h11.pos=0 OR h11.pos IS NULL))
FULL OUTER JOIN objectproductionplacegroup opp ON (h11.id=opp.id)

FULL OUTER JOIN hierarchy h12 ON (h12.parentid = cc.id AND h12.name = 'collectionobjects_common:objectProductionDateGroupList'  AND (h12.pos=0 OR h12.pos IS NULL))
FULL OUTER JOIN structureddategroup pd ON (pd.id = h12.id)

FULL OUTER JOIN hierarchy h13 ON (h13.parentid = cc.id AND h13.name='collectionobjects_common:materialGroupList' AND (h13.pos=0 OR h13.pos IS NULL))
FULL OUTER JOIN materialgroup matg ON (h13.id = matg.id)

FULL OUTER JOIN hierarchy htig on (cc.id = htig.parentid AND htig.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList' AND (htig.pos=0 OR htig.pos IS NULL))
FULL OUTER JOIN taxonomicIdentGroup tig ON (tig.id = htig.id)

FULL OUTER JOIN hierarchy h14 ON (h14.parentid = cc.id AND h14.name = 'collectionobjects_common:contentDateGroup'  AND (h14.pos=0 OR h14.pos IS NULL))
FULL OUTER JOIN structureddategroup ddep ON (ddep.id = h14.id)

FULL OUTER JOIN hierarchy h15 ON (cc.id=h15.parentid AND h15.name='collectionobjects_common:objectProductionPersonGroupList' AND (h15.pos=0 OR h15.pos IS NULL))
FULL OUTER JOIN objectproductionpersongroup ope ON (h15.id=ope.id)

left outer join collectionobjects_common_responsibledepartments rd on (rd.id=cc.id and rd.pos=0)

join misc ms on (cc.id=ms.id and ms.lifecyclestate <> 'deleted')
""" + whereclause + """
ORDER BY sortableobjectnumber
limit """ + str(num2ret)

    objects = setupcursor(config, getobjects)
    #for object in objects.fetchall():
    #print(object)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()], None


def findcurrentlocation(csid, config):

    getloc = "select findcurrentlocation('" + csid + "')"

    try:
        objects = setupcursor(config, getloc)
    except:
        return "findcurrentlocation error"

    return objects.fetchone()[0]


def getrefname(table, term, config):

    if term == None or term == '':
        return ''

    if table in ('collectionobjects_common_fieldcollectors', 'collectionobjects_common_briefdescriptions',
                 'acquisitions_common_owners'):
        column = 'item'
    else:
        column = 'refname'

    if table == 'collectionobjects_common_briefdescriptions':
        query = "SELECT item FROM collectionobjects_common_briefdescriptions WHERE item ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    elif table == 'pahmaaltnumgroup':
        query = "SELECT pahmaaltnum FROM pahmaaltnumgroup WHERE pahmaaltnum ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    elif table == 'pahmaaltnumgroup_type':
        query = "SELECT pahmaaltnumtype FROM pahmaaltnumgroup WHERE pahmaaltnum ILIKE '%s' LIMIT 1" % (
            term.replace("'", "''"))
    else:
        query = "select %s from %s x join misc ON misc.id = x.id AND misc.lifecyclestate <> 'deleted' where %s ILIKE '%%''%s''%%' LIMIT 1" % (
            column, table, column, term.replace("'", "''"))

    try:
        objects = setupcursor(config, query)
        return objects.fetchone()[0]
    except:
        return ''
        raise


def findrefnames(table, termlist, config):

    result = []
    for t in termlist:
        query = "select refname from %s where refname ILIKE '%%''%s''%%'" % (table, t.replace("'", "''"))

        try:
            objects = setupcursor(config, query)
            refname = objects.fetchone()
            result.append([t, refname])
        except:
            raise
            return "findrefnames error"

    return result

def finddoctypes(table, doctype, config):

    query = "select %s,count(*) as n from %s group by %s;" % (doctype,table,doctype)

    try:
        doctypes = setupcursor(config,query)
        # return doctypes.fetchall()
        return [list(item) for item in doctypes.fetchall()]
    except:
        raise
        return "finddoctypes error"


def getobjinfo(museumNumber, config):

    getobjects = """
    SELECT co.objectnumber,
    n.objectname,
    co.numberofobjects,
    regexp_replace(fcp.item, '^.*\\)''(.*)''$', '\\1') AS fieldcollectionplace,
    regexp_replace(apg.assocpeople, '^.*\\)''(.*)''$', '\\1') AS culturalgroup,
    regexp_replace(pef.item, '^.*\\)''(.*)''$', '\\1') AS  ethnographicfilecode
FROM collectionobjects_common co
LEFT OUTER JOIN hierarchy h1 ON (co.id = h1.parentid AND h1.primarytype='objectNameGroup' AND h1.pos=0)
LEFT OUTER JOIN objectnamegroup n ON (n.id=h1.id)
LEFT OUTER JOIN collectionobjects_pahma_pahmafieldcollectionplacelist fcp ON (co.id=fcp.id AND fcp.pos=0)
LEFT OUTER JOIN collectionobjects_pahma_pahmaethnographicfilecodelist pef on (pef.id=co.id and pef.pos=0)
LEFT OUTER JOIN collectionobjects_common_responsibledepartments cm ON (co.id=cm.id AND cm.pos=0)
LEFT OUTER JOIN hierarchy h2 ON (co.id=h2.parentid AND h2.primarytype='assocPeopleGroup' AND h2.pos=0)
LEFT OUTER JOIN assocpeoplegroup apg ON apg.id=h2.id
JOIN misc ON misc.id = co.id AND misc.lifecyclestate <> 'deleted'
WHERE co.objectnumber = '%s' LIMIT 1""" % museumNumber

    objects = setupcursor(config, getobjects)
    #for ob in objects.fetchone():
    #print(ob)
    return objects.fetchone()


def gethierarchy(query, config):
    institution = config.get('info', 'institution')

    if query == 'taxonomy':
        gethierarchy = """
SELECT DISTINCT
        regexp_replace(child.refname, '^.*\\)''(.*)''$', '\\1') AS Child, 
        regexp_replace(parent.refname, '^.*\\)''(.*)''$', '\\1') AS Parent, 
        h1.name AS ChildKey,
        h2.name AS ParentKey
FROM taxon_common child
JOIN misc ON (misc.id = child.id)
FULL OUTER JOIN hierarchy h1 ON (child.id = h1.id)
FULL OUTER JOIN relations_common rc ON (h1.name = rc.subjectcsid)
FULL OUTER JOIN hierarchy h2 ON (rc.objectcsid = h2.name)
FULL OUTER JOIN taxon_common parent ON (parent.id = h2.id)
WHERE child.refname LIKE 'urn:cspace:%s.cspace.berkeley.edu:taxonomyauthority:name(taxon):item:name%%'
AND misc.lifecyclestate <> 'deleted'
ORDER BY Parent, Child
""" % institution
    elif query != 'places':
        gethierarchy = """
SELECT DISTINCT
        regexp_replace(child.refname, '^.*\\)''(.*)''$', '\\1') AS Child, 
        regexp_replace(parent.refname, '^.*\\)''(.*)''$', '\\1') AS Parent, 
        h1.name AS ChildKey,
        h2.name AS ParentKey
FROM concepts_common child
JOIN misc ON (misc.id = child.id)
FULL OUTER JOIN hierarchy h1 ON (child.id = h1.id)
FULL OUTER JOIN relations_common rc ON (h1.name = rc.subjectcsid)
FULL OUTER JOIN hierarchy h2 ON (rc.objectcsid = h2.name)
FULL OUTER JOIN concepts_common parent ON (parent.id = h2.id)
WHERE child.refname LIKE 'urn:cspace:%s.cspace.berkeley.edu:conceptauthorities:name({0})%%'
AND misc.lifecyclestate <> 'deleted'
ORDER BY Parent, Child""" % institution
        gethierarchy = gethierarchy.format(query)
    else:
        if institution == 'pahma': tenant = 'Tenant15'
        if institution == 'botgarden': tenant = 'Tenant35'
        gethierarchy = """
SELECT DISTINCT
	regexp_replace(tc.refname, '^.*\\)''(.*)''$', '\\1') Place,
	regexp_replace(tc2.refname, '^.*\\)''(.*)''$', '\\1') ParentPlace,
	h.name ChildKey,
	h2.name ParentKey
FROM public.places_common tc
	INNER JOIN misc m ON (tc.id=m.id AND m.lifecyclestate<>'deleted')
	INNER JOIN hierarchy h ON (tc.id = h.id AND h.primarytype='Placeitem%s')
	LEFT OUTER JOIN public.relations_common rc ON (h.name = rc.subjectcsid)
	LEFT OUTER JOIN hierarchy h2 ON (h2.primarytype = 'Placeitem%s' AND rc.objectcsid = h2.name)
	LEFT OUTER JOIN places_common tc2 ON (tc2.id = h2.id)
ORDER BY ParentPlace, Place""" % (tenant, tenant)

    objects = setupcursor(config, gethierarchy)
    #return objects.fetchall()
    return [list(item) for item in objects.fetchall()]


def getCSID(argType, arg, config):

    if argType == 'objectnumber':
        query = """SELECT h.name from collectionobjects_common cc
JOIN hierarchy h on h.id=cc.id
WHERE objectnumber = '%s'""" % arg.replace("'", "''")
    elif argType == 'crateName':
        query = """SELECT h.name FROM collectionobjects_anthropology ca
JOIN hierarchy h on h.id=ca.id
WHERE computedcrate ILIKE '%%''%s''%%'""" % arg.replace("'", "''")
    elif argType == 'placeName':
        query = """SELECT h.name from places_common pc
JOIN hierarchy h on h.id=pc.id
WHERE pc.refname ILIKE '%""" + arg.replace("'", "''") + "%%'"

    objects = setupcursor(config, query)
    return objects.fetchone()


def getCSIDs(argType, arg, config):

    if argType == 'crateName':
        query = """SELECT h.name FROM collectionobjects_anthropology ca
JOIN hierarchy h on h.id=ca.id
WHERE computedcrate ILIKE '%%''%s''%%'""" % arg.replace("'", "''")

    objects = setupcursor(config, query)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()]


def findparents(refname, config):

    query = """WITH RECURSIVE ethnculture_hierarchyquery as (
SELECT regexp_replace(cc.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCulture,
      cc.refname,
      rc.objectcsid broaderculturecsid,
      regexp_replace(cc2.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCultureBroader,
      0 AS level
FROM concepts_common cc
JOIN hierarchy h ON (cc.id = h.id)
LEFT OUTER JOIN relations_common rc ON (h.name = rc.subjectcsid)
LEFT OUTER JOIN hierarchy h2 ON (rc.relationshiptype='hasBroader' AND rc.objectcsid = h2.name)
LEFT OUTER JOIN concepts_common cc2 ON (cc2.id = h2.id)
WHERE cc.refname LIKE 'urn:cspace:pahma.cspace.berkeley.edu:conceptauthorities:name(concept)%%'
and cc.refname = '%s'
UNION ALL
SELECT regexp_replace(cc.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCulture,
      cc.refname,
      rc.objectcsid broaderculturecsid,
      regexp_replace(cc2.refname, '^.*\\)''(.*)''$', '\\1') AS ethnCultureBroader,
      ech.level-1 AS level
FROM concepts_common cc
JOIN hierarchy h ON (cc.id = h.id)
LEFT OUTER JOIN relations_common rc ON (h.name = rc.subjectcsid)
LEFT OUTER JOIN hierarchy h2 ON (rc.relationshiptype='hasBroader' AND rc.objectcsid = h2.name)
LEFT OUTER JOIN concepts_common cc2 ON (cc2.id = h2.id)
INNER JOIN ethnculture_hierarchyquery AS ech ON h.name = ech.broaderculturecsid)
SELECT ethnCulture, refname, level
FROM ethnculture_hierarchyquery
order by level""" % refname.replace("'", "''")

    try:
        objects = setupcursor(config, query)
        # return objects.fetchall()
        return [list(item) for item in objects.fetchall()]
    except:
        #raise
        return [["findparents error"]]

def getCSIDDetail(config, csid, detail):
    
    if detail == 'fieldcollectionplace':
        query = """SELECT substring(pfc.item, position(')''' IN pfc.item)+2, LENGTH(pfc.item)-position(')''' IN pfc.item)-2)
AS fieldcollectionplace

FROM collectionobjects_pahma_pahmafieldcollectionplacelist pfc
LEFT OUTER JOIN HIERARCHY h1 on (pfc.id=h1.id and pfc.pos = 0)

WHERE h1.name = '%s'""" % csid
    elif detail == 'assocpeoplegroup':
        query = """SELECT substring(apg.assocpeople, position(')''' IN apg.assocpeople)+2, LENGTH(apg.assocpeople)-position(')''' IN apg.assocpeople)-2)
as culturalgroup

FROM collectionobjects_common cc

left outer join hierarchy h1 on (cc.id=h1.id)
left outer join hierarchy h2 on (cc.id=h2.parentid and h2.primarytype =
'assocPeopleGroup' and (h2.pos=0 or h2.pos is null))
left outer join assocpeoplegroup apg on (apg.id=h2.id)

WHERE h1.name = '%s'""" % csid
    elif detail == 'objcount':
        query = """SELECT cc.numberofobjects
FROM collectionobjects_common cc
left outer join hierarchy h1 on (cc.id=h1.id)
WHERE h1.name = '%s'""" % csid
    elif detail == 'objNumber':
        query = """SELECT cc.objectnumber
FROM collectionobjects_common cc
left outer join hierarchy h1 on (cc.id=h1.id)
WHERE h1.name = '%s'""" % csid
    elif detail == 'material':
        pass
    elif detail == 'taxon':
        pass
    else:
        return ''
    try:
        objects = setupcursor(config, query)
        return objects.fetchone()[0]
    except:
        return ''


def getSitesByOwner(config, owner):

    query = """SELECT DISTINCT REGEXP_REPLACE(fcp.item, '^.*\)''(.*)''$', '\\1') AS "site",
    REGEXP_REPLACE(pog.anthropologyplaceowner, '^.*\)''(.*)''$', '\\1') AS "site owner",
    pog.anthropologyplaceownershipnote AS "ownership note",
    pc.placenote AS "place note"
FROM collectionobjects_pahma_pahmafieldcollectionplacelist fcp 
JOIN places_common pc ON (pc.refname = fcp.item)
JOIN misc ms ON (ms.id = pc.id AND ms.lifecyclestate <> 'deleted')
JOIN hierarchy h1 ON (h1.parentid = pc.id AND h1.name = 'places_anthropology:anthropologyPlaceOwnerGroupList')
JOIN anthropologyplaceownergroup pog ON (pog.id = h1.id)
WHERE pog.anthropologyplaceowner LIKE '%%""" + owner.replace("'", "''") + """%%'
ORDER BY REGEXP_REPLACE(fcp.item, '^.*\)''(.*)''$', '\\1')"""
    objects = setupcursor(config,query)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()]


def getDisplayName(config, refname):


    query = """SELECT REGEXP_REPLACE(pog.anthropologyplaceowner, '^.*\)''(.*)''$', '\\1')
FROM anthropologyplaceownergroup pog
WHERE pog.anthropologyplaceowner LIKE '""" + refname + "%'"

    objects = setupcursor(config,query)
    return objects.fetchone()

def getObjDetailsByOwner(config, owner):

    query = """SELECT DISTINCT cc.objectnumber AS "Museum No.",
    cp.sortableobjectnumber AS "sort number",
    cc.numberofobjects AS "pieces",
    ong.objectname AS "object name",
    fcd.datedisplaydate AS "collection date",
    STRING_AGG(DISTINCT(ac.acquisitionreferencenumber), ', ') AS "Acc. No.",
    REGEXP_REPLACE(fcp.item, '^.*\)''(.*)''$', '\\1') AS "site",
    REGEXP_REPLACE(pog.anthropologyplaceowner, '^.*\)''(.*)''$', '\\1') AS "site owner",
    pog.anthropologyplaceownershipnote AS "ownership note", pc.placenote AS "place note"
FROM collectionobjects_common cc
JOIN collectionobjects_pahma cp ON (cc.id = cp.id)
JOIN collectionobjects_pahma_pahmafieldcollectionplacelist fcp ON (fcp.id = cc.id)
JOIN misc ms ON (ms.id = cc.id AND ms.lifecyclestate <> 'deleted')
JOIN places_common pc ON (pc.refname = fcp.item)
JOIN hierarchy h1 ON (h1.parentid = pc.id AND h1.name = 'places_anthropology:anthropologyPlaceOwnerGroupList')
JOIN anthropologyplaceownergroup pog ON (pog.id = h1.id)
FULL OUTER JOIN hierarchy h2 ON (h2.parentid = cc.id AND h2.name = 'collectionobjects_common:objectNameList' AND h2.pos = 0)
FULL OUTER JOIN objectnamegroup ong ON (ong.id = h2.id)
FULL OUTER JOIN hierarchy h3 ON (h3.id = cc.id)
FULL OUTER JOIN relations_common rc ON (rc.subjectcsid = h3.name AND rc.objectdocumenttype = 'Acquisition')
FULL OUTER JOIN hierarchy h4 ON (h4.name = rc.objectcsid)
FULL OUTER JOIN acquisitions_common ac ON (ac.id = h4.id)
FULL OUTER JOIN hierarchy h5 ON (h5.parentid = cc.id AND h5.pos = 0 AND h5.name = 'collectionobjects_pahma:pahmaFieldCollectionDateGroupList')
FULL OUTER JOIN structureddategroup fcd ON (fcd.id = h5.id)
WHERE REGEXP_REPLACE(pog.anthropologyplaceowner, '^.*\)''(.*)''$', '\\1') ILIKE '%""" + owner + """%'
OR (pog.anthropologyplaceowner IS NULL AND pog.anthropologyplaceownershipnote ILIKE '%""" + owner + """%')
GROUP BY cc.objectnumber, cp.sortableobjectnumber, cc.numberofobjects, ong.objectname, fcd.datedisplaydate, fcp.item, pog.anthropologyplaceowner, pog.anthropologyplaceownershipnote, pc.placenote
ORDER BY REGEXP_REPLACE(fcp.item, '^.*\)''(.*)''$', '\\1'), pog.anthropologyplaceownershipnote, cp.sortableobjectnumber
"""

    objects = setupcursor(config,query)
    # return objects.fetchall()
    return [list(item) for item in objects.fetchall()]
