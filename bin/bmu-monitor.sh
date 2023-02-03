#!/bin/bash

source ${HOME}/pipeline-config.sh

# NB: BAM no longer uses the BMU: they use a DAMS, currently "ResourceSpace" to push to / pull from CSpace
for t in botgarden cinefiles pahma ucjeps; do python3 /var/www/$t/uploadmedia/checkRuns.py ${HOMEDIR}/bmu/$t jobs summary $t > /var/www/static/${t}.nightly.report.txt ; done
# bmu 'usage graphs': plots of nightly bmu uploads
bash -l -c 'python3 /var/www/pahma/uploadmedia/bmu-nightly-2022-concise.py /cspace/monitor > /dev/null'
python3 /var/www/pahma/uploadmedia/checkRuns.py ${HOMEDIR}/bmu/pahma jobs summary pahma | mail -r "cspace-support@lists.berkeley.edu" -s "recent PAHMA BMU jobs" pahma-cspace-bmu@lists.berkeley.edu > /dev/null 2>&1
python3 /var/www/ucjeps/uploadmedia/checkRuns.py ${HOMEDIR}/bmu/ucjeps jobs summary ucjeps | mail -r "cspace-support@lists.berkeley.edu" -s "recent UCJEPS BMU jobs" ucjeps-it@berkeley.edu > /dev/null 2>&1
python3 /var/www/cinefiles/uploadmedia/checkRuns.py ${HOMEDIR}/bmu/cinefiles jobs summary cinefiles | mail -r "cspace-support@lists.berkeley.edu" -s "recent Cinefiles BMU jobs" bampfacspaceuploader@lists.berkeley.edu > /dev/null 2>&1
python3 /var/www/botgarden/uploadmedia/checkRuns.py ${HOMEDIR}/bmu/botgarden jobs summary botgarden | mail -r "cspace-support@lists.berkeley.edu" -s "recent UCBG BMU jobs" ucbg-cspace-bmu@lists.berkeley.edu > /dev/null 2>&1
##################################################################################
# keep a set of the BMU log files
##################################################################################
for t in bampfa botgarden cinefiles pahma ucjeps
do
  cp -p /cspace/bmu/${t}/*.csv /cspace/monitor/image_upload_cache_${t}/ > /dev/null 2>&1
  cp -p /cspace/bmu/${t}/*.trace.log /cspace/monitor/image_upload_cache_${t}/ > /dev/null 2>&1
done
