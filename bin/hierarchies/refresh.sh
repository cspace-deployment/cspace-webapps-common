#!/bin/bash -x

source ${HOME}/pipeline-config.sh

HOSTNAME="${PAHMA_SERVER}"
USERNAME="nuxeo_pahma"
DATABASE="pahma_domain_pahma"
CONNECTSTRING="host=$HOSTNAME dbname=$DATABASE sslmode=require"
time psql -U $USERNAME -d "$CONNECTSTRING" -c "select utils.refreshculturehierarchytable();"
time psql -U $USERNAME -d "$CONNECTSTRING" -c "select utils.refreshmaterialhierarchytable();"
time psql -U $USERNAME -d "$CONNECTSTRING" -c "select utils.refreshtaxonhierarchytable();"
time psql -U $USERNAME -d "$CONNECTSTRING" -c "select utils.refreshobjectclasshierarchytable();"
time psql -U $USERNAME -d "$CONNECTSTRING" -c "select utils.refreshobjectplacelocationtable();"

cd ${HOME}/bin/hierarchies ; ./checkstatus.sh pahma | mail -r "cspace-support@lists.berkeley.edu" -s "hierarchies refresh" "${PAHMA_CONTACT}"
