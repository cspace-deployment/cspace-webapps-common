rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${HOME}/extracts/cch/*.gz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${HOME}/extracts/major_group/*.gz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${HOME}/extracts/taxonauth/*.gz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${HOME}/extracts/ucjeps-authorities/authorities.tgz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
source ${HOME}/pipeline-config.sh
rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${SOLR_CACHE_DIR}/4solr.ucjeps.public.csv.gz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
rsync -v -e "ssh -i ${HOME}/.ssh/id_rsa" ${SOLR_CACHE_DIR}/4solr.ucjeps.media.csv.gz cspace@cynips.bnhm.berkeley.edu:/usr/local/web/ucjeps_web/cspace/
