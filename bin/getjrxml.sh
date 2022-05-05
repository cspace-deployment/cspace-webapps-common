#!/bin/bash
# this script refreshes the webapps jrxml directory with all the report jrxml
# the ireport webapp needs them!
rm -rf ${HOME}/services
# make the directory if it doesn't exist
if [ ! -d ${HOMEDIR}/jrxml ]
then
   mkdir ${HOMEDIR}/jrxml
fi
git clone https://github.com/cspace-deployment/services.git
cd ${HOME}/services
git checkout origin/bampfa_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
git checkout origin/botgarden_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
git checkout origin/cinefiles_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
git checkout origin/pahma_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
git checkout origin/ucjeps_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
cd
rm -rf ${HOME}/services
