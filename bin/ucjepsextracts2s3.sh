#!/bin/bash
# Replaces rsync2annie.sh with a push mechanism to S3 for AWS.

source ${HOME}/pipeline-config.sh

EXTRACTSDIR="${HOMEDIR}/extracts"

source ~/bin/set_environment.sh || { echo 'could not set environment set_environment.sh failed'; exit 1; }

/usr/bin/aws s3 rm s3://cspace-extracts-${ENVIRONMENT} --quiet --recursive --exclude "*" --include "ucjeps/*"

/usr/bin/aws s3 sync ${EXTRACTSDIR}/cch s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress \
                 --exclude "*" --include "*.gz"
/usr/bin/aws s3 sync ${EXTRACTSDIR}/major_group s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress \
                 --exclude "*" --include "*.gz"
/usr/bin/aws s3 sync ${EXTRACTSDIR}/taxonauth s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress \
                 --exclude "*" --include "*.gz"

/usr/bin/aws s3 cp ${EXTRACTSDIR}/ucjeps_soft-deletes.tab.gz s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress
/usr/bin/aws s3 cp ${EXTRACTSDIR}/ucjeps-authorities/authorities.tgz s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress
/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.public.csv.gz s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress
# allmedia is ... well ... all the media files; media is just those 'media only' files found in the media portal
/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.media.csv.gz s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress
/usr/bin/aws s3 cp ${SOLR_CACHE_DIR}/4solr.ucjeps.allmedia.csv.gz s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress

# Since S3 is not a traditional filesystem, directory browsing is not possible in the traditional sense.
# Instead we create a file named MANIFEST.TXT that contains URLs to all the items in the bucket for
# a given object prefix (dev, qa, or prod).
# Then one only needs to know the URL for the manifest to get a list of the rest of the objects.
# manifest URL is https://cspace-extracts-prod.s3.us-west-2.amazonaws.com/ucjeps/MANIFEST.TXT
# For example:
# wget -qO- https://cspace-extracts-prod.s3.us-west-2.amazonaws.com/ucjeps/MANIFEST.TXT | xargs -n1 wget
/usr/bin/aws s3api list-objects --bucket "cspace-extracts-${ENVIRONMENT}" --prefix "ucjeps/" | \
/usr/bin/jq -r '.Contents[].Key' | \
/usr/bin/sed "s/^/https:\/\/cspace-extracts-${ENVIRONMENT}.s3.us-west-2.amazonaws.com\//" > \
/tmp/MANIFEST.TXT

/usr/bin/aws s3 cp /tmp/MANIFEST.TXT s3://cspace-extracts-${ENVIRONMENT}/ucjeps/ \
                 --no-progress

echo "Extracts copied to S3"
echo
echo "(These links will work if you are signed in to the UCB VPN)"
echo
cat /tmp/MANIFEST.TXT

/usr/bin/rm -f /tmp/MANIFEST.TXT

