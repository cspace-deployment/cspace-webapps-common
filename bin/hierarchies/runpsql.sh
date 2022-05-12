#!/bin/bash -x

source ${HOME}/pipeline-config.sh

TENANT=$1
USERNAME="$4_${TENANT}"
HOSTNAME="dba-postgres-prod-45.ist.berkeley.edu port=$2 sslmode=prefer"
DATABASE="${TENANT}_domain_${TENANT}"
CONNECTSTRING="host=$HOSTNAME dbname=$DATABASE sslmode=require"
psql -e -a -U $USERNAME -d "$CONNECTSTRING" -f $3
