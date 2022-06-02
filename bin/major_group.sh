#!/bin/bash

source ${HOME}/pipeline-config.sh
YYMMDD=`date +%y%m%d`

HOST="${UCJEPS_SERVER}"
# NB: port is now part of the HOST parameter, see pipeline-config.sh
DBNAME="ucjeps_domain_ucjeps"
DBUSER="reporter_ucjeps"
CONNECTSTRING="host=$HOST dbname=$DBNAME sslmode=prefer"

MG_DIR=${HOMEDIR}/extracts/major_group
MG_LOG=${MG_DIR}/major_group.log
MG_FILE=${MG_DIR}/major_group.txt

if [ ! -d "${MG_DIR}" ]; then
	mkdir ${MG_DIR}
	echo "Made directory ${MG_DIR}"
fi

# remove previous file, if any
rm -f $MG_FILE

echo 'query START time: ' `date` >> $MG_LOG

psql -d "$CONNECTSTRING" -U $DBUSER << HP_END >> $MG_LOG

create temp table tmp_major_group_accn as
select
	co.objectnumber as accession_num,
	tu.taxonmajorgroup as major_group,
	createdby as created_by,
	date(createdat) as created_date,
	updatedby as updated_by,
	date(updatedat) as updatedi_date
from collectionobjects_common co
left outer join hierarchy h
	on (co.id = h.parentid and h.pos = 0
		and h.name = 'collectionobjects_naturalhistory:taxonomicIdentGroupList')
left outer join taxonomicIdentGroup tig on (tig.id = h.id)
left outer join taxon_common tc on (tc.refname = tig.taxon)
left outer join taxon_ucjeps tu on (tu.id = tc.id)
join collectionspace_core csc on (csc.id = co.id)
join misc m on (m.id = co.id and m.lifecyclestate != 'deleted')
where co.objectnumber not like '%test%'
order by objectnumber;

\copy (select * from tmp_major_group_accn order by accession_num) to '$MG_FILE' with null as ''

HP_END

echo 'query END time: ' `date` >> $MG_LOG

ls -l $MG_FILE >> $MG_LOG

wc -l $MG_FILE >> $MG_LOG

gzip -c $MG_FILE > $MG_FILE.gz

ls -l *.gz >> $MG_LOG

rm -f $MG_FILE

echo '' >> $MG_LOG
