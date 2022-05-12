#!/bin/bash -x

source ${HOME}/pipeline-config.sh

HOSTNAME="${PAHMA_SERVER}"
USERNAME="nuxeo_pahma"
DATABASE="pahma_domain_pahma"
CONNECTSTRING="host=$HOSTNAME dbname=$DATABASE sslmode=require"
psql -U $USERNAME -d "$CONNECTSTRING" -f checkstatus.sql
