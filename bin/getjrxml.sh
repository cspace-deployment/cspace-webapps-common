#!/bin/bash
# this script refreshes the webapps jrxml directory with all the report jrxml
# the ireport webapp needs them!
rm -rf ${HOME}/services
# make the directory if it doesn't exist
if [ ! -d ${HOMEDIR}/jrxml ]
then
   mkdir ${HOMEDIR}/jrxml
fi
git clone https://github.com/cspace-deployment/services.git ${HOME}/services
cd ${HOME}/services
git checkout origin/ucb_6.0
# copy 'core' reports
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ${HOMEDIR}/jrxml
# copy reports for all tenants
cp services/report/3rdparty/jasper-cs-report/src/main/resources/tenants/*/*.jrxml ${HOMEDIR}/jrxml
cd
rm -rf ${HOME}/services
