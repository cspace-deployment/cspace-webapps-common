#!/bin/bash

# locate job
JOB=$1
ORIGINAL=$(find /cspace/bmu/ -name "${JOB}.original.csv")
if [[ -f ${ORIGINAL} ]]; then
  echo found ${ORIGINAL}, starting rerun
else
  echo job files for "${JOB}" not found, cannot rerun
  exit 1
fi
BMU_DIR=$(dirname ${ORIGINAL})
MUSEUM=$(basename "${BMU_DIR}")
PROCESSED=$(find /cspace/bmu/ -name "${JOB}.processed.csv")
if [[ -f ${PROCESSED} ]]; then
  echo found "${PROCESSED}", saving media csids in "${BMU_DIR}/${JOB}.savedmediacsids.csv"
  # make list of media csids
  cut -f16 "${PROCESSED}" | grep -v mediaCSID > "${BMU_DIR}/${JOB}.savedmediacsids.csv"
else
  echo "${JOB}" does not seem to have completed, cannot rerun
  exit 1
fi
# set up job to run again
STEP1=${ORIGINAL/original/step1}
JOB_PREFIX=${ORIGINAL/.original.csv/}
#cp ${ORIGINAL} ${STEP1}
# TODO for now, for ucjeps, we must reinstate the original CR2 names
perl -pe 's/.JPG/.CR2/' ${ORIGINAL} > ${STEP1}
echo saving job files...
for f in original.csv processed.csv trace.log
do
  mv "${BMU_DIR}/${JOB}.${f}" "${BMU_DIR}/${JOB}.saved${f}"
done
# run it
echo starting bmu re-rerun
time /var/www/${MUSEUM}/uploadmedia/postblob.sh ${MUSEUM} ${JOB_PREFIX} uploadmedia_batch  >> /cspace/bmu/${MUSEUM}/batches.log 2>&1
# set env vars (using bmu config file)
perl -pe 's/ *= */=/g;s/^(\w+)/export \1/;s/^\[/#[/' /var/www/ucjeps/config/uploadmedia_batch.cfg > /tmp/bmu.cfg
source /tmp/bmu.cfg
rm /tmp/bmu.cfg
echo "deleting `wc -l ${BMU_DIR}/${JOB}.savedmediacsids.csv | cut -f1 -d " "` previous images"
for CSID in `cat ${BMU_DIR}/${JOB}.savedmediacsids.csv`
do
  echo curl -S --stderr - -X DELETE https://${hostname}/cspace-services/media/$CSID --basic -u "<redacted>"
  curl -S --stderr - -X DELETE https://${hostname}/cspace-services/media/$CSID --basic -u "${username}:${password}"
done
# tidy up
