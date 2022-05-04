# Replaces rsync2annie.sh with a push mechanism to S3 for AWS.
#!/bin/bash

EXTRACTSDIR="/cspace/extracts"
BL_ENVIRONMENT=`/usr/bin/curl -s -m 5 http://169.254.169.254/latest/meta-data/tags/instance/BL_ENVIRONMENT`

if [[ -z $BL_ENVIRONMENT || ( "$BL_ENVIRONMENT" != "dev" && "$BL_ENVIRONMENT" != "qa" && "$BL_ENVIRONMENT" != "prod" ) ]]; then
	echo "Could not fetch BL_ENVIRONMENT, are you sure you're on AWS?"
	exit 1
fi

source ${HOME}/pipeline-config.sh

/usr/bin/aws s3 rm s3://ucjepsextracts/ --recursive --exclude "*" --include "${BL_ENVIRONMENT}/*"

/usr/bin/aws s3 cp ${EXTRACTSDIR}/cch/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/major_group/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/taxonauth/*.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${EXTRACTSDIR}/ucjeps-authorities/authorities.tgz s3://ucjepsextracts/${BL_ENVIRONMENT}/

/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.public.csv.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/
/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.media.csv.gz s3://ucjepsextracts/${BL_ENVIRONMENT}/

# Since S3 is not a traditional filesystem, directory browsing is not possible in the traditional sense.
# Instead we create a file named MANIFEST.TXT that contains URLs to all the items in the bucket for 
# a given object prefix (dev, qa, or prod).
# Then one only needs to know the URL for the manifest to get a list of the rest of the objects.
# manifest URL is https://ucjepsextracts.s3.us-west-2.amazonaws.com/${BL_ENVIRONMENT}/MANIFEST.TXT
# For example:
# wget -qO- https://ucjepsextracts.s3.us-west-2.amazonaws.com/dev/MANIFEST.TXT | xargs -n1 wget
/usr/bin/aws s3api list-objects --bucket "ucjepsextracts" --prefix "${BL_ENVIRONMENT}/" | \
/usr/bin/jq -r '.Contents[].Key' | \
/usr/bin/sed "s/^${BL_ENVIRONMENT}\//https:\/\/ucjepsextracts.s3.us-west-2.amazonaws.com\/${BL_ENVIRONMENT}\//" > \
/tmp/MANIFEST.TXT

/usr/bin/aws s3 cp /tmp/MANIFEST.TXT s3://ucjepsextracts/${BL_ENVIRONMENT}/

/usr/bin/rm -f /tmp/MANIFEST.TXT

