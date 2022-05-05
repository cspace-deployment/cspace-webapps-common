#!/usr/bin/env bash

WORKINGDIR="${HOMEDIR}/extracts/ucjeps-authorities"
# make the directory if it doesn't exist
if [ ! -d ${WORKINGDIR} ]
then
   mkdir -p ${WORKINGDIR}
fi
${HOME}/bin/extract_authorities.sh orgauthorities/225e44ef-7f3d-4660-a4d6 ${WORKINGDIR}/nomenclature.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh orgauthorities/751023ec-d953-45f9-a0a8 ${WORKINGDIR}/determination.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh orgauthorities/a71f4ab6-221a-4202-bf75 ${WORKINGDIR}/institution.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh orgauthorities/dcba2506-20fd-438b-9adc ${WORKINGDIR}/typeassertion.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh orgauthorities/f53284f1-0462-4326-92e7 ${WORKINGDIR}/organizationtest.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh orgauthorities/6d89bda7-867a-4b97-b22f ${WORKINGDIR}/organization.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
${HOME}/bin/extract_authorities.sh personauthorities/492326d1-efb1-4d2b-96d9 ${WORKINGDIR}/person.xml 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
# taxonomy is too big, and this data is already being extracted via SQL for the CCH project
# ${HOME}/bin/extract_authorities.sh taxonomyauthority/87036424-e55f-4e39-bd12 ${WORKINGDIR}/taxonomyauthority.xml
# out with the old, in with the new...
cd
tar -czf /tmp/authorities.tgz ${WORKINGDIR} 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
mv /tmp/authorities.tgz ${WORKINGDIR}/authorities.tgz 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]'
