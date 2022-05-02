#!/bin/bash

EXTRACTSDIR="/cspace/extracts"
BL_ENVIRONMENT=`/usr/bin/curl -s -m 5 http://169.254.169.254/latest/meta-data/tags/instance/BL_ENVIRONMENT`

if [[ -z $BL_ENVIRONMENT || ( "$BL_ENVIRONMENT" != "dev" && "$BL_ENVIRONMENT" != "qa" && "$BL_ENVIRONMENT" != "prod" ) ]]; then
	echo "Could not fetch BL_ENVIRONMENT, are you sure you're on AWS?"
	exit 1
fi

source ${HOME}/pipeline-config.sh

/usr/bin/aws s3 cp ${EXTRACTSDIR}/cch/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/major_group/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/taxonauth/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/ucjeps-authorities/authorities.tgz s3://ucjepsextracts/${BL_ENVIRONMENT}/

/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.public.csv.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.media.csv.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
